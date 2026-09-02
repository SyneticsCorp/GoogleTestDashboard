"""!
@file test_query_state_navigation.py
@brief Integration test for FR-033: list state survives a list -> detail -> list round trip.
"""
import os
import re

import pytest

from _template_capture import capturedTemplateContext as _capturedTemplateContext
from gtestdash.web.app import createApp

## Real, read-only dataset root; never modified by tests (CLAUDE.md).
_resultsRoot = os.path.join(os.path.dirname(__file__), "..", "..", "GoogleTestResults")


@pytest.fixture
def dashboardApp():
    """!
    @brief A real Flask app wired to the read-only GoogleTestResults dataset.
    @return The created Flask app (not yet queried).
    """
    return createApp(_resultsRoot)


def test_searchRoute_pageTwoFailedOnly_restoresSameListStateAfterVisitingTestDetail(dashboardApp):
    """!
    @brief FR-033 acceptance: visiting a test from page 2 of a filtered search and
           following its "목록으로 돌아가기" link restores identical query/filter/page state.
    """
    client = dashboardApp.test_client()

    with _capturedTemplateContext(dashboardApp) as listCaptured:
        client.get("/search?status=FAILED&page=2")
    originalRow = listCaptured[0]["testRows"][0]
    assert "returnUrl=" in originalRow["testUrl"]

    with _capturedTemplateContext(dashboardApp) as detailCaptured:
        detailResponse = client.get(originalRow["testUrl"])
    returnUrl = detailCaptured[0]["returnUrl"]
    detailBody = detailResponse.get_data(as_text=True)

    with _capturedTemplateContext(dashboardApp) as restoredCaptured:
        client.get(returnUrl)
    restored = restoredCaptured[0]

    assert detailResponse.status_code == 200
    assert 'class="back-to-list-link"' in detailBody
    assert restored["statusFilter"] == "FAILED"
    assert restored["page"] == 2
    assert restored["testRows"][0]["testName"] == originalRow["testName"]


def test_buildDetailRoute_noReturnUrlOnDirectVisit_testDetailFallsBackToBuildDetail(dashboardApp):
    """!
    @brief FR-033: without a returnUrl (e.g. reached from the dashboard's own
           failure list), the test-detail "돌아가기" link falls back to the
           owning build's detail page.
    """
    with _capturedTemplateContext(dashboardApp) as dashboardCaptured:
        dashboardApp.test_client().get("/")
    failureRow = dashboardCaptured[0]["latestFailures"][0]
    assert "returnUrl=" not in failureRow["testUrl"]

    response = dashboardApp.test_client().get(failureRow["testUrl"])
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert re.search(r'<a class="back-to-list-link" href="/builds/10">', body)
