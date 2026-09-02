"""!
@file test_navigation_breadcrumbs.py
@brief Integration tests for FR-032: every detail page can reach its parent
       page without the browser's back button, via a working breadcrumb link.
"""
import os
import re

import pytest

from gtestdash.web.app import createApp
from gtestdash.web.routes.route_helpers import buildTestDetailUrl

## Real, read-only dataset root; never modified by tests (CLAUDE.md).
_resultsRoot = os.path.join(os.path.dirname(__file__), "..", "..", "GoogleTestResults")


@pytest.fixture
def dashboardApp():
    """!
    @brief A real Flask app wired to the read-only GoogleTestResults dataset.
    @return The created Flask app (not yet queried).
    """
    return createApp(_resultsRoot)


def _crumbHrefs(body):
    """!
    @brief Extract every href inside the page's crumb-nav breadcrumb region.
    @param body Rendered HTML page body.
    @return List of href attribute values found inside the first <nav class="crumb-nav">.
    """
    navMatch = re.search(r'<nav class="crumb-nav">(.*?)</nav>', body, re.DOTALL)
    assert navMatch, "expected a crumb-nav breadcrumb region on this page"
    return re.findall(r'href="([^"]+)"', navMatch.group(1))


def test_buildDetail_breadcrumb_linksBackToDashboard(dashboardApp):
    """!
    @brief FR-032: build-detail's breadcrumb can navigate back to the main dashboard.
    """
    client = dashboardApp.test_client()

    response = client.get("/builds/10")
    hrefs = _crumbHrefs(response.get_data(as_text=True))

    assert hrefs == ["/"]
    assert client.get(hrefs[0]).status_code == 200


def test_moduleDetail_breadcrumb_linksBackToDashboardAndBuildDetail(dashboardApp):
    """!
    @brief FR-032: module-detail's breadcrumb can navigate back to both the
           main dashboard and the owning build's detail page.
    """
    client = dashboardApp.test_client()

    response = client.get("/builds/10/modules/ChildLockController")
    hrefs = _crumbHrefs(response.get_data(as_text=True))

    assert hrefs == ["/", "/builds/10"]
    assert all(client.get(href).status_code == 200 for href in hrefs)


def test_testDetail_breadcrumb_linksBackToDashboardBuildAndModule(dashboardApp):
    """!
    @brief FR-032: test-detail's breadcrumb can navigate back to the main
           dashboard, the owning build, and the owning module.
    """
    client = dashboardApp.test_client()
    record = next(r for r in dashboardApp.config["SNAPSHOT"].records if r.build_id == "10")

    response = client.get(buildTestDetailUrl(record))
    hrefs = _crumbHrefs(response.get_data(as_text=True))

    assert hrefs == ["/", "/builds/10", f"/builds/10/modules/{record.module}"]
    assert all(client.get(href).status_code == 200 for href in hrefs)


def test_searchResults_breadcrumb_linksBackToDashboard(dashboardApp):
    """!
    @brief FR-032: the search-results page's breadcrumb can navigate back to
           the main dashboard.
    """
    client = dashboardApp.test_client()

    response = client.get("/search")
    hrefs = _crumbHrefs(response.get_data(as_text=True))

    assert hrefs == ["/"]
    assert client.get(hrefs[0]).status_code == 200


def test_fullDrilldownChain_mainToBuildToModuleToTest_everyStepReachable(dashboardApp):
    """!
    @brief FR-032 acceptance: the 메인 -> 빌드 상세 -> 모듈 상세 -> 테스트 상세
           forward navigation chain is fully reachable end to end.
    """
    client = dashboardApp.test_client()

    assert client.get("/").status_code == 200
    assert client.get("/builds/10").status_code == 200
    assert client.get("/builds/10/modules/ChildLockController").status_code == 200
    record = next(
        r for r in dashboardApp.config["SNAPSHOT"].records
        if r.build_id == "10" and r.module == "ChildLockController"
    )
    assert client.get(buildTestDetailUrl(record)).status_code == 200
