"""!
@file test_dashboard_route.py
@brief Integration tests for GET / against the real dataset (FR-009~017, Requirements.md §7).
"""
import os
from contextlib import contextmanager

import pytest
from flask import template_rendered

from gtestdash.web.app import createApp

## Real, read-only dataset root; never modified by tests (CLAUDE.md).
_resultsRoot = os.path.join(os.path.dirname(__file__), "..", "..", "GoogleTestResults")

## Expected per-build failure rate percentages, build 01 through 10, per §7.
_expectedFailureRatesByBuild = [8, 4, 9, 6, 3, 7, 5, 10, 4, 2]


@contextmanager
def _capturedTemplateContext(app):
    """!
    @brief Capture the context dict passed to render_template() during a request.
    @param app Flask app instance whose template_rendered signal to observe.
    @return List that will hold one context dict per template render, in order.
    """
    captured = []

    def _record(_sender, template, context, **_extra):
        captured.append(context)

    template_rendered.connect(_record, app)
    try:
        yield captured
    finally:
        template_rendered.disconnect(_record, app)


@pytest.fixture
def dashboardApp():
    """!
    @brief A real Flask app wired to the read-only GoogleTestResults dataset.
    @return The created Flask app (not yet queried).
    """
    return createApp(_resultsRoot)


def test_dashboardRoute_returnsOk(dashboardApp):
    """!
    @brief GET / responds 200 (basic route wiring smoke check).
    """
    response = dashboardApp.test_client().get("/")

    assert response.status_code == 200


def test_dashboardRoute_showsLatestBuildSummary(dashboardApp):
    """!
    @brief §7/FR-010: build 10 summary is 1200 total / 1176 passed / 24 failed / 2.0%.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/")

    latest = captured[0]["latestSummary"]
    assert latest["buildId"] == "10"
    assert latest["total"] == 1200
    assert latest["passed"] == 1176
    assert latest["failed"] == 24
    assert latest["failureRate"] == 2.0


def test_dashboardRoute_showsDecreaseVsPreviousBuild(dashboardApp):
    """!
    @brief FR-011 acceptance: build 10 vs 09 is a 2.0pp decrease, 4.0% -> 2.0%.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/")

    diff = captured[0]["buildDiff"]
    assert diff["direction"] == "decrease"
    assert diff["failureRateDiff"] == -2.0
    assert diff["previousFailureRate"] == 4.0


def test_dashboardRoute_trendMatchesExpectedFailureRateSequence(dashboardApp):
    """!
    @brief FR-012 acceptance: builds 01..10 trend as 8,4,9,6,3,7,5,10,4,2 percent.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/")

    trendPoints = captured[0]["trendPoints"]
    assert [point["failureRate"] for point in trendPoints] == _expectedFailureRatesByBuild


def test_dashboardRoute_moduleDistribution_latestScopeSumsToTwentyFour(dashboardApp):
    """!
    @brief FR-014 acceptance: default (latest) scope's failures sum to 24.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/")

    distribution = captured[0]["moduleDistribution"]
    assert sum(entry["failed"] for entry in distribution) == 24


def test_dashboardRoute_moduleDistribution_cumulativeScopeSumsToSixHundredNinetySix(dashboardApp):
    """!
    @brief FR-014 acceptance: cumulative scope's failures sum to 696 (CLAUDE.md).
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/?scope=cumulative")

    distribution = captured[0]["moduleDistribution"]
    assert sum(entry["failed"] for entry in distribution) == 696


def test_dashboardRoute_showsTwentyFourLatestFailures(dashboardApp):
    """!
    @brief FR-016 acceptance: the latest build's failure list has 24 entries.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/")

    assert len(captured[0]["latestFailures"]) == 24


def test_dashboardRoute_showsTenBuildHistoryRows(dashboardApp):
    """!
    @brief FR-017 acceptance: the build history table lists all 10 builds, latest first.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/")

    buildHistory = captured[0]["buildHistory"]
    assert len(buildHistory) == 10
    assert buildHistory[0]["buildId"] == "10"
