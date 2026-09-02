"""!
@file test_e2e_fr032_036_navigation_state_refresh_errors.py
@brief Browser E2E tests transcribed from TestCase_Template.xlsx for
       TS-FR-032 (page-to-page navigation path), TS-FR-033 (list state
       preservation across a detail visit), TS-FR-034 (refresh), TS-FR-035
       (corrupted XML resilience) and TS-FR-036 (empty-result guidance).

Covers TC-FR-032-01/02/03/04, TC-FR-033-01/02, TC-FR-034-01, TC-FR-035-01/02,
TC-FR-036-01 (none tagged "(제안)"). TC-FR-035's synthetic corrupted-XML
scenario reuses the malformed.xml fixture tests/integration already relies
on, via the corruptedXmlServerUrl fixture (see conftest.py) -- the xlsx
itself flags this pair "※ 사용자 확인 필요(가상 손상 데이터)".
"""
import pytest
from playwright.sync_api import expect


@pytest.mark.e2e
def test_tcFr03201_dashboardToBuildDetail(page, liveServerUrl):
    """!
    @brief TC-FR-032-01: selecting build 10 from the main page's build
           history navigates to /builds/10 (FR-032).
    """
    page.goto(liveServerUrl + "/")
    page.locator(".build-history-table a", has_text="10").first.click()
    page.wait_for_url("**/builds/10")


@pytest.mark.e2e
def test_tcFr03202_buildDetailToModuleDetail(page, liveServerUrl):
    """!
    @brief TC-FR-032-02: selecting ChildLockController from the build-detail
           module table navigates to /builds/10/modules/ChildLockController
           (FR-032).
    """
    page.goto(liveServerUrl + "/builds/10")
    page.locator(".module-table a", has_text="ChildLockController").click()
    page.wait_for_url("**/builds/10/modules/ChildLockController")


@pytest.mark.e2e
def test_tcFr03203_moduleDetailToTestDetail(page, liveServerUrl):
    """!
    @brief TC-FR-032-03: selecting any row from the module-detail test list
           navigates to /builds/10/modules/ChildLockController/.../tests/...
           (FR-032).
    """
    page.goto(liveServerUrl + "/builds/10/modules/ChildLockController")
    page.locator(".tests-table tbody tr").first.locator("a").click()
    page.wait_for_url("**/builds/10/tests/**")


@pytest.mark.e2e
def test_tcFr03204_onScreenBackLinksReturnUpTheHierarchyWithoutBrowserBack(page, liveServerUrl):
    """!
    @brief TC-FR-032-04: from a test-detail page, on-screen links alone
           (never the browser's back button) return through module detail →
           build detail → main (FR-032).
    """
    page.goto(liveServerUrl + "/builds/10/modules/ChildLockController")
    page.locator(".tests-table tbody tr").first.locator("a").click()
    expect(page.locator("#test-summary-heading")).to_be_visible()

    page.locator("a.back-to-list-link").click()
    page.wait_for_url("**/builds/10/modules/ChildLockController*")

    page.locator(".crumb-nav a", has_text="빌드 10").click()
    page.wait_for_url("**/builds/10")

    page.locator(".crumb-nav a", has_text="메인").click()
    page.wait_for_url(liveServerUrl + "/")


## TC-FR-033's "small pageSize to reach page 2" list state. The xlsx's own
## example URL uses pageSize=10, which is not one of FR-031's supported
## sizes (25/50/100) and falls back to 50 -- and build 10 alone only has 24
## failed tests, too few for any supported size to ever reach a page 2.
## /search's cross-build failedOnly view (696 failures) is used instead, with
## the smallest supported size (25), to reach a genuine page 2 while keeping
## the same failedOnly+page+pageSize intent the TC describes.
_pageTwoFailedOnlyUrl = "/search?failedOnly=true&page=2&pageSize=25"


@pytest.mark.e2e
def test_tcFr03301_navigateToTestDetailFromPageTwoOfFailedOnlyView(page, liveServerUrl):
    """!
    @brief TC-FR-033-01: from a small-page-size, failed-only, page-2 view,
           opening a test's detail page succeeds (FR-033).
    """
    page.goto(liveServerUrl + _pageTwoFailedOnlyUrl)
    expect(page.locator(".tests-table tbody tr")).to_have_count(25)

    # The search table's row has two links (build id, then test name) --
    # the test name is the one that opens the detail page.
    page.locator(".tests-table tbody tr").first.locator("a").last.click()
    expect(page.locator("#test-summary-heading")).to_be_visible()


@pytest.mark.e2e
def test_tcFr03302_returningFromDetailRestoresFilterAndPageState(page, liveServerUrl):
    """!
    @brief TC-FR-033-02: "목록으로 돌아가기" from that test's detail page
           restores the exact same failedOnly/page/pageSize list state
           (FR-033).
    """
    page.goto(liveServerUrl + _pageTwoFailedOnlyUrl)
    page.locator(".tests-table tbody tr").first.locator("a").last.click()

    page.locator("a.back-to-list-link").click()

    expect(page.locator('input[name="failedOnly"]')).to_be_checked()
    expect(page.locator(".pagination-range")).to_contain_text("페이지 2")
    expect(page.locator(".tests-table tbody tr")).to_have_count(25)


@pytest.mark.e2e
def test_tcFr03401_refreshButtonCompletesAndKeepsAggregatesConsistent(page, liveServerUrl):
    """!
    @brief TC-FR-034-01: clicking the refresh button (POST /refresh) succeeds
           without error, and re-renders the same dashboard aggregates for
           the unchanged dataset (FR-034).
    """
    page.goto(liveServerUrl + "/")
    beforeTotal = page.locator(".latest-summary .stat-tile", has_text="전체").locator("dd").inner_text()

    response = page.locator(".refresh-form button[type='submit']").click()
    expect(page.locator("#latest-summary-heading")).to_contain_text("10")
    afterTotal = page.locator(".latest-summary .stat-tile", has_text="전체").locator("dd").inner_text()

    assert afterTotal == beforeTotal == "1200"


@pytest.mark.e2e
def test_tcFr03501_corruptedXmlLeavesOtherNineFilesRenderedAndListsExclusion(page, corruptedXmlServerUrl):
    """!
    @brief TC-FR-035-01: with one malformed XML injected into build 10, the
           other 9 real files' results still render, and the corrupted file
           appears in an excluded-files/warning list with its path and a
           parse-error reason (FR-035, §8-7).
    """
    page.goto(corruptedXmlServerUrl + "/builds/10")

    expect(page.locator(".warning-banner")).to_be_visible()
    warningText = page.locator(".warning-banner").inner_text()
    assert "gtest_malformed_injected.xml" in warningText
    # The malformed file is an 11th file injected alongside the 10 real
    # modules (not a replacement of one), so all 10 real modules' 1,200
    # records still contribute -- only the corrupt file's own 0 records are
    # excluded.
    expect(page.locator(".stat-tile", has_text="전체")).to_contain_text("1200")
    expect(page.locator(".module-table tbody tr")).to_have_count(10)


@pytest.mark.e2e
def test_tcFr03502_appKeepsServingOtherPagesWithCorruptedXmlPresent(page, corruptedXmlServerUrl):
    """!
    @brief TC-FR-035-02: with the same corrupted XML present, the app process
           keeps serving other pages without crashing (§8 조건7, FR-035).
    """
    for path in ("/", "/search", "/builds/05", "/builds/10"):
        response = page.goto(corruptedXmlServerUrl + path)
        assert response.status == 200


@pytest.mark.e2e
def test_tcFr03601_zeroSearchMatchesShowsGuidanceNotAnEmptyTable(page, liveServerUrl):
    """!
    @brief TC-FR-036-01 (boundary): a search matching nothing shows
           cause-and-next-action guidance instead of a blank table, and does
           not raise an error (FR-036).
    """
    response = page.goto(liveServerUrl + "/search?q=zzz_no_such_test_20260902")

    assert response.status == 200
    expect(page.locator(".empty-state")).to_contain_text("조건에 맞는 테스트가 없습니다")
    expect(page.locator(".empty-state")).to_contain_text("검색어나 필터를 조정")
    expect(page.locator(".tests-table")).to_have_count(0)
