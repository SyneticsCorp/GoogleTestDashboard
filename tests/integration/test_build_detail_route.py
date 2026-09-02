"""!
@file test_build_detail_route.py
@brief Integration tests for GET /builds/<build_id> against the real dataset (FR-018, FR-019).
"""
import os
from contextlib import contextmanager

import pytest
from flask import template_rendered

from gtestdash.web.app import createApp

## Real, read-only dataset root; never modified by tests (CLAUDE.md).
_resultsRoot = os.path.join(os.path.dirname(__file__), "..", "..", "GoogleTestResults")


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


def test_buildDetailRoute_unknownBuildId_returns404(dashboardApp):
    """!
    @brief GET /builds/<unknown> responds 404 (FR-018).
    """
    response = dashboardApp.test_client().get("/builds/99")

    assert response.status_code == 404


def test_buildDetailRoute_knownBuildId_returnsOk(dashboardApp):
    """!
    @brief GET /builds/10 responds 200 for a known build (FR-018).
    """
    response = dashboardApp.test_client().get("/builds/10")

    assert response.status_code == 200


def test_buildDetailRoute_firstBuild_hasNoPreviousBuildLink(dashboardApp):
    """!
    @brief FR-018 acceptance: build "01" has no previous-build navigation.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/builds/01")

    assert captured[0]["prevBuildId"] is None
    assert captured[0]["nextBuildId"] == "02"


def test_buildDetailRoute_lastBuild_hasNoNextBuildLink(dashboardApp):
    """!
    @brief FR-018 acceptance: build "10" has no next-build navigation.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/builds/10")

    assert captured[0]["nextBuildId"] is None
    assert captured[0]["prevBuildId"] == "09"


def test_buildDetailRoute_build10_listsAllTwelveHundredTestRecordsWithNoFilter(dashboardApp):
    """!
    @brief FR-019/FR-031 acceptance: build 10 with no filter matches all 1,200 records,
           paginated 50 per page (24 pages) rather than rendered all at once.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/builds/10")

    assert captured[0]["totalMatches"] == 1200
    assert captured[0]["totalPages"] == 24
    assert len(captured[0]["testRows"]) == 50


def test_buildDetailRoute_build10_summaryMatchesFR010Figures(dashboardApp):
    """!
    @brief Build detail's summary reuses the same counts as the main dashboard (FR-010, FR-018).
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/builds/10")

    summary = captured[0]["buildSummary"]
    assert summary["total"] == 1200
    assert summary["passed"] == 1176
    assert summary["failed"] == 24
    assert summary["failureRate"] == 2.0


def test_buildDetailRoute_build10_moduleDistributionHasTenModulesSummingToTwentyFourFailures(dashboardApp):
    """!
    @brief §7.1 acceptance: build 10's ten modules' failures sum to 24.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/builds/10")

    distribution = captured[0]["moduleDistribution"]
    assert len(distribution) == 10
    assert sum(entry["failed"] for entry in distribution) == 24


def test_buildDetailRoute_build10_failedOnlyToggle_matchesExactlyTwentyFourTests(dashboardApp):
    """!
    @brief FR-025 acceptance: build 10's failed-only toggle matches exactly 24 tests.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/builds/10?failedOnly=true")

    assert captured[0]["totalMatches"] == 24
    assert all(row["status"] == "FAILED" for row in captured[0]["testRows"])
