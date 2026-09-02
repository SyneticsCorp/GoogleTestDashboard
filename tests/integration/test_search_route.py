"""!
@file test_search_route.py
@brief Integration tests for GET /search against the real dataset (FR-026~031).
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


def test_searchRoute_returnsOk(dashboardApp):
    """!
    @brief GET /search responds 200 even with no query params (FR-026).
    """
    response = dashboardApp.test_client().get("/search")

    assert response.status_code == 200


def test_searchRoute_noQuery_matchesEveryRecord(dashboardApp):
    """!
    @brief FR-029 "전체 초기화" acceptance: no query params matches all 12,000 records.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/search")

    assert captured[0]["totalMatches"] == 12000


def test_searchRoute_evaluateLockRequest_returnsMatchingFunctionAndTestName(dashboardApp):
    """!
    @brief FR-026 acceptance: searching "EvaluateLockRequest" returns that function/test name.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/search?q=EvaluateLockRequest")

    assert captured[0]["totalMatches"] > 0
    assert all(
        "evaluatelockrequest" in (row["function"] + row["testName"]).lower()
        for row in captured[0]["testRows"]
    )


def test_searchRoute_buildAndModuleAndFailedOnly_matchesExactlyThreeAcceptanceRecords(dashboardApp):
    """!
    @brief FR-029 acceptance: build 10 + ChildLockController + failed-only matches 3 records.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get(
            "/search?buildId=10&module=ChildLockController&failedOnly=true"
        )

    assert captured[0]["totalMatches"] == 3
    assert all(row["status"] == "FAILED" for row in captured[0]["testRows"])
    assert all(row["module"] == "ChildLockController" for row in captured[0]["testRows"])


def test_searchRoute_filterOptions_excludeNonexistentFixedValues(dashboardApp):
    """!
    @brief FR-028 acceptance: no nonexistent module/suite value ever appears in filterOptions.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/search?buildId=10&module=ChildLockController")

    options = captured[0]["filterOptions"]
    assert "DoesNotExistModule" not in options["module"]
    assert options["module"] == ["ChildLockController"]


def test_searchRoute_defaultPageSize_showsTwentyFourPagesForTwelveThousandRecords(dashboardApp):
    """!
    @brief FR-031 acceptance: 12,000 (or a build-scoped 1,200) results paginate at 50/page.
    """
    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get("/search?buildId=10")

    assert captured[0]["totalMatches"] == 1200
    assert captured[0]["totalPages"] == 24
    assert captured[0]["pageSize"] == 50
    assert captured[0]["displayRange"] == "1-50"
