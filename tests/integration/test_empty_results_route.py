"""!
@file test_empty_results_route.py
@brief Integration tests for FR-036: zero-result and zero-failure pages show
       cause-and-next-action guidance instead of an empty table, with no
       exceptions or chart errors.
"""
import os

import pytest

from _template_capture import capturedTemplateContext as _capturedTemplateContext

from gtestdash.web.app import createApp

## Real, read-only dataset root; never modified by tests (CLAUDE.md).
_realResultsRoot = os.path.join(os.path.dirname(__file__), "..", "..", "GoogleTestResults")
## Read-only single-build fixture with zero failing tests (FR-036); never modified.
_zeroFailuresRoot = os.path.join(
    os.path.dirname(__file__), "..", "fixtures", "edge_cases", "zero_failures_build"
)


@pytest.fixture
def zeroFailuresApp():
    """!
    @brief A Flask app wired to a fixture build tree with zero failing tests.
    @return The created Flask app (not yet queried).
    """
    return createApp(_zeroFailuresRoot)


@pytest.fixture
def realDataApp():
    """!
    @brief A Flask app wired to the real, read-only GoogleTestResults dataset.
    @return The created Flask app (not yet queried).
    """
    return createApp(_realResultsRoot)


def test_dashboardRoute_buildWithNoFailures_showsNoFailuresMessageAndNoException(zeroFailuresApp):
    """!
    @brief FR-036 acceptance: a build with zero failures shows "실패 테스트
           없음" instead of an empty table, and the page renders without error.
    """
    with _capturedTemplateContext(zeroFailuresApp) as captured:
        response = zeroFailuresApp.test_client().get("/")

    assert response.status_code == 200
    assert captured[0]["latestFailures"] == []
    assert "실패 테스트 없음" in response.get_data(as_text=True)


def test_dashboardRoute_buildWithNoFailures_moduleChartDataIsWellFormedZeroState(zeroFailuresApp):
    """!
    @brief FR-036 acceptance: the module failure chart's data is a well-formed
           zero-failure list (not missing/undefined), so Chart.js can render a
           0-state bar chart without erroring.
    """
    with _capturedTemplateContext(zeroFailuresApp) as captured:
        zeroFailuresApp.test_client().get("/")

    distribution = captured[0]["moduleDistribution"]
    assert distribution
    assert all(entry["failed"] == 0 for entry in distribution)


def test_searchRoute_noMatchingQuery_showsGuidanceInsteadOfEmptyTable(realDataApp):
    """!
    @brief FR-036 acceptance: a search with no matches shows cause + next-action
           guidance rather than an empty table, and does not error.
    """
    response = realDataApp.test_client().get("/search?q=존재하지않는검색어XYZ123")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "조건에 맞는 테스트가 없습니다" in body
    assert "검색어나 필터를 조정" in body


def test_buildDetailRoute_filterMatchesNothing_showsGuidanceInsteadOfEmptyTable(realDataApp):
    """!
    @brief FR-036 acceptance: a build-detail filter combination matching zero
           tests shows the same guidance, rather than an empty table.
    """
    response = realDataApp.test_client().get("/builds/10?q=존재하지않는검색어XYZ123")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "조건에 맞는 테스트가 없습니다" in body
