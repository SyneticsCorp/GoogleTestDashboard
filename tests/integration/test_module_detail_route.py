"""!
@file test_module_detail_route.py
@brief Integration tests for GET /builds/<build_id>/modules/<module> against the real dataset (FR-020, FR-021).
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


def test_moduleDetailRoute_unknownModule_returns404(dashboardApp):
    """!
    @brief GET /builds/10/modules/<unknown> responds 404 (FR-020).
    """
    response = dashboardApp.test_client().get("/builds/10/modules/DoesNotExist")

    assert response.status_code == 404


def test_moduleDetailRoute_unknownBuildId_returns404(dashboardApp):
    """!
    @brief GET /builds/<unknown>/modules/<known-module> responds 404 (FR-020).
    """
    response = dashboardApp.test_client().get("/builds/99/modules/ChildLockController")

    assert response.status_code == 404


def test_moduleDetailRoute_knownCombination_returnsOk(dashboardApp):
    """!
    @brief GET /builds/10/modules/ChildLockController responds 200 for a valid combination.
    """
    response = dashboardApp.test_client().get("/builds/10/modules/ChildLockController")

    assert response.status_code == 200


def test_moduleDetailRoute_build10EachModule_showsAllOneHundredTwentyTests(dashboardApp):
    """!
    @brief §7.1/FR-020 acceptance: each of build 10's modules has 120 total tests.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/builds/10/modules/ChildLockController")

    assert captured[0]["moduleSummary"]["total"] == 120


def test_moduleDetailRoute_childLockControllerBuild10_noFilterShowsOneHundredTwentyTests(dashboardApp):
    """!
    @brief FR-021 acceptance: no filter on build 10's ChildLockController shows 120 tests.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/builds/10/modules/ChildLockController")

    assert len(captured[0]["testRows"]) == 120


def test_moduleDetailRoute_childLockControllerBuild10_matchesThreeFailuresPerAcceptanceTable(dashboardApp):
    """!
    @brief §7.1 acceptance: build 10's ChildLockController has exactly 3 failures.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/builds/10/modules/ChildLockController")

    assert captured[0]["moduleSummary"]["failed"] == 3


def test_moduleDetailRoute_functionFilter_narrowsTestRows(dashboardApp):
    """!
    @brief FR-021: a ?function= filter narrows testRows to that function only.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/builds/10/modules/ChildLockController")
    allRows = captured[0]["testRows"]
    oneFunction = allRows[0]["function"]

    with _capturedTemplateContext(dashboardApp) as filteredCaptured:
        dashboardApp.test_client().get(f"/builds/10/modules/ChildLockController?function={oneFunction}")

    filteredRows = filteredCaptured[0]["testRows"]
    assert 0 < len(filteredRows) < len(allRows)
    assert all(row["function"] == oneFunction for row in filteredRows)


def test_moduleDetailRoute_trend_coversAllTenBuildsForThatModule(dashboardApp):
    """!
    @brief FR-020: moduleTrend spans every build the module appears in, not just the viewed one.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/builds/10/modules/ChildLockController")

    trend = captured[0]["moduleTrend"]
    assert [point["buildId"] for point in trend] == [f"{n:02d}" for n in range(1, 11)]
