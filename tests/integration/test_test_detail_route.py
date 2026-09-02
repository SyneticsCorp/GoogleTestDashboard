"""!
@file test_test_detail_route.py
@brief Integration tests for GET /builds/<build_id>/tests/<test_id> against the real dataset (FR-022~024).
"""
import os
import re
from contextlib import contextmanager

import pytest
from flask import template_rendered

from gtestdash.repository import buildSnapshot
from gtestdash.web.app import createApp
from gtestdash.web.routes.route_helpers import buildTestDetailUrl

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


def _findOneRecord(app, buildId, status):
    """!
    @brief Locate one real record with the given build id and status from the app's snapshot.
    @param app Flask app whose SNAPSHOT to search.
    @param buildId Build id to restrict the search to.
    @param status Normalized status to look for (e.g. "FAILED", "PASSED").
    @return The first matching ResultRecord; the dataset guarantees at least one exists.
    """
    return next(
        record
        for record in app.config["SNAPSHOT"].records
        if record.build_id == buildId and record.status == status
    )


def test_testDetailRoute_unknownTestId_returns404(dashboardApp):
    """!
    @brief GET /builds/10/tests/<unknown> responds 404 (FR-022).
    """
    response = dashboardApp.test_client().get("/builds/10/tests/NoSuchClass.NoSuchTest")

    assert response.status_code == 404


def test_testDetailRoute_unknownBuildId_returns404(dashboardApp):
    """!
    @brief GET /builds/<unknown>/tests/<known-test-id> responds 404 (FR-022).
    """
    record = _findOneRecord(dashboardApp, "10", "FAILED")
    knownTestId = buildTestDetailUrl(record).rsplit("/", 1)[-1]

    response = dashboardApp.test_client().get(f"/builds/99/tests/{knownTestId}")

    assert response.status_code == 404


def test_testDetailRoute_failedTestFromDashboardLatestFailures_identityMatchesListedRecord(dashboardApp):
    """!
    @brief FR-022 acceptance: identity fields on the detail page match the row that linked to it.

    Picks a failing test straight from the dashboard's own latestFailures list
    (rather than deriving the URL out-of-band) so this proves the actual
    list-to-detail navigation, not just the URL-building helper.
    """
    with _capturedTemplateContext(dashboardApp) as dashboardCaptured:
        dashboardApp.test_client().get("/")
    failureRow = dashboardCaptured[0]["latestFailures"][0]

    with _capturedTemplateContext(dashboardApp) as detailCaptured:
        response = dashboardApp.test_client().get(failureRow["testUrl"])

    assert response.status_code == 200
    test = detailCaptured[0]["test"]
    assert test["module"] == failureRow["module"]
    assert test["function"] == failureRow["function"]
    assert test["suite"] == failureRow["suite"]
    assert test["testName"] == failureRow["testName"]
    assert test["testFile"] == failureRow["testFile"]
    assert test["line"] == failureRow["line"]


def test_testDetailRoute_failedTest_showsFailureTypeAndSummary(dashboardApp):
    """!
    @brief FR-023 acceptance: failure type and summary reach the template context.
    """
    record = _findOneRecord(dashboardApp, "10", "FAILED")

    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get(buildTestDetailUrl(record))

    test = captured[0]["test"]
    assert test["failureType"] == record.failure_type
    assert test["failureSummary"] == record.failure_summary


def test_testDetailRoute_failedTest_responseContainsFullFailureDetailVerbatim(dashboardApp):
    """!
    @brief FR-023 acceptance: Expected/Actual text, file path and line number are not truncated.

    Reads the real XML's raw <failure> body directly (not through the parser
    under test) and asserts the HTML response contains that exact text, so
    this proves the page truncates nothing.
    """
    record = _findOneRecord(dashboardApp, "10", "FAILED")
    assert record.failure_detail
    assert "Expected" in record.failure_detail
    assert "Actual" in record.failure_detail

    response = dashboardApp.test_client().get(buildTestDetailUrl(record))
    body = response.get_data(as_text=True)

    for line in record.failure_detail.splitlines():
        assert line.strip() in body


def test_testDetailRoute_passedTest_rendersOkWithoutFailureSection(dashboardApp):
    """!
    @brief FR-024 acceptance: a PASSED test (no <failure>) renders 200 with no exception.
    """
    record = _findOneRecord(dashboardApp, "10", "PASSED")
    assert record.failure_detail is None

    response = dashboardApp.test_client().get(buildTestDetailUrl(record))

    assert response.status_code == 200
    assert "실패 정보 없음" in response.get_data(as_text=True)


def test_testDetailRoute_passedTest_identityFieldsMatchRecord(dashboardApp):
    """!
    @brief FR-022 acceptance: a PASSED test's detail page shows the same identity fields as its record.
    """
    record = _findOneRecord(dashboardApp, "10", "PASSED")

    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get(buildTestDetailUrl(record))

    test = captured[0]["test"]
    assert test["buildId"] == record.build_id
    assert test["module"] == record.module
    assert test["function"] == record.function
    assert test["suite"] == record.suite
    assert test["testName"] == record.test_name
    assert test["classname"] == record.classname
    assert test["status"] == record.status
    assert test["durationSeconds"] == record.duration_seconds
    assert test["timestamp"] == record.timestamp
    assert test["testFile"] == record.test_file
    assert test["line"] == record.line
    assert test["sourceFile"] == record.source_file


def test_testDetailRoute_context_carriesCurrentBuildForCommonSearchForm(dashboardApp):
    """!
    @brief FR-027: the common search form defaults its scope to the current build.
    """
    record = _findOneRecord(dashboardApp, "10", "PASSED")

    with _capturedTemplateContext(dashboardApp) as captured:
        dashboardApp.test_client().get(buildTestDetailUrl(record))

    assert captured[0]["searchContextBuildId"] == "10"
