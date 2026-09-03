"""!
@file test_e2e_fr025_031_search_filter_sort_page.py
@brief Browser E2E tests transcribed from TestCase_Template.xlsx for
       TS-FR-025 (failed-only toggle), TS-FR-026 (common search), TS-FR-027
       (context-scoped search), TS-FR-028 (filter option generation),
       TS-FR-029 (combined search+filter / reset), TS-FR-030 (sorting) and
       TS-FR-031 (pagination).

Covers every TC under these TS_IDs (none tagged "(제안)"): TC-FR-025-01/02,
TC-FR-026-01/02/03, TC-FR-027-01/02/03, TC-FR-028-01/02, TC-FR-029-01/02,
TC-FR-030-01/02/03, TC-FR-031-01/02/03.
"""
from urllib.parse import quote

import pytest
from playwright.sync_api import expect


def _totalMatches(page, headingSelector):
    """!
    @brief Parse the "(...건)" count out of a list page's own heading.
    @param page Playwright page with a list route already loaded.
    @param headingSelector CSS selector for that page's own results heading.
    @return The parsed integer match count.
    """
    heading = page.locator(headingSelector).inner_text()
    return int(heading.split("(")[1].split("건")[0].replace(",", ""))


@pytest.mark.e2e
def test_tcFr02501_buildTenFailedOnlyShowsExactlyTwentyFour(page, liveServerUrl):
    """!
    @brief TC-FR-025-01: /builds/10?failedOnly=true shows exactly 24 rows,
           all FAILED (§7, §8-5, FR-025).
    """
    page.goto(liveServerUrl + "/builds/10?failedOnly=true")

    rows = page.locator(".tests-table tbody tr")
    expect(rows).to_have_count(24)
    statuses = rows.locator("td:first-child").all_inner_texts()
    assert all(status == "FAILED" for status in statuses)


@pytest.mark.e2e
def test_tcFr02502_failedOnlyToggleWorksOnModuleAndSearchPagesToo(page, liveServerUrl):
    """!
    @brief TC-FR-025-02: the failed-only toggle also narrows the module-
           detail page (ChildLockController → 3) and the search page (every
           row FAILED) (FR-025).
    """
    page.goto(liveServerUrl + "/builds/10/modules/ChildLockController?failedOnly=true")
    expect(page.locator(".tests-table tbody tr")).to_have_count(3)

    page.goto(liveServerUrl + "/search?failedOnly=true")
    statuses = page.locator(".tests-table tbody tr td:first-child").all_inner_texts()
    assert statuses and all(status == "FAILED" for status in statuses)


@pytest.mark.e2e
def test_tcFr02601_searchByFunctionNameReturnsMatches(page, liveServerUrl):
    """!
    @brief TC-FR-026-01: searching "EvaluateLockRequest" returns matching
           results (FR-026).
    """
    page.goto(liveServerUrl + "/search?q=EvaluateLockRequest")
    assert _totalMatches(page, "#search-results-heading") > 0


@pytest.mark.e2e
def test_tcFr02602_searchIsCaseInsensitive(page, liveServerUrl):
    """!
    @brief TC-FR-026-02: an all-lowercase query returns the exact same
           result count as TC-FR-026-01's mixed-case query (FR-026).
    """
    page.goto(liveServerUrl + "/search?q=EvaluateLockRequest")
    mixedCaseCount = _totalMatches(page, "#search-results-heading")

    page.goto(liveServerUrl + "/search?q=evaluatelockrequest")
    lowerCaseCount = _totalMatches(page, "#search-results-heading")

    assert lowerCaseCount == mixedCaseCount > 0


@pytest.mark.e2e
def test_tcFr02603_searchCoversModuleNameAndFailureSummaryFields(page, liveServerUrl):
    """!
    @brief TC-FR-026-03: searching by module name returns results, and
           searching by a failure summary's own substring returns the
           originating failed test (FR-026).
    """
    page.goto(liveServerUrl + "/search?q=ChildLockController")
    assert _totalMatches(page, "#search-results-heading") > 0

    page.goto(liveServerUrl + "/builds/10?failedOnly=true")
    firstFailedRow = page.locator(".tests-table tbody tr").first
    testName = firstFailedRow.locator("td").nth(4).inner_text()
    firstFailedRow.locator("a").click()
    failureSummary = page.locator(".stat-tile", has_text="실패 요약").locator("dd").inner_text()
    summaryFragment = failureSummary.strip()

    # Scoped to build 10 (this is where the originating record lives) and a
    # generous pageSize, since the same synthetic summary text can recur
    # across other builds/modules and would otherwise push it off page 1.
    page.goto(f"{liveServerUrl}/search?buildId=10&pageSize=100&q={quote(summaryFragment)}")
    resultTestNames = page.locator(".tests-table tbody tr td:nth-child(6)").all_inner_texts()
    assert testName in resultTestNames


@pytest.mark.e2e
def test_tcFr02701_buildDetailSearchDefaultsToThatBuild(page, liveServerUrl):
    """!
    @brief TC-FR-027-01: searching from /builds/10 opens /search with the
           build filter defaulted to 10, so other builds' matches never mix
           in (FR-027).
    """
    page.goto(liveServerUrl + "/builds/10")
    page.locator(".search-form input[name='q']").fill("EvaluateLockRequest")
    page.locator(".search-form button[type='submit']").click()

    page.wait_for_url("**/search*")
    expect(page.locator("#build-filter")).to_have_value("10")
    buildIdCells = page.locator(".tests-table tbody tr td:nth-child(2)").all_inner_texts()
    assert all(value == "10" for value in buildIdCells)


@pytest.mark.e2e
def test_tcFr02702_moduleDetailSearchDefaultsToThatBuildAndModule(page, liveServerUrl):
    """!
    @brief TC-FR-027-02: searching from a module-detail page defaults both
           the build and module filters to the current context (FR-027).
    """
    page.goto(liveServerUrl + "/builds/10/modules/ChildLockController")
    page.locator(".search-form input[name='q']").fill("Evaluate")
    page.locator(".search-form button[type='submit']").click()

    page.wait_for_url("**/search*")
    expect(page.locator("#build-filter")).to_have_value("10")
    moduleCells = page.locator(".tests-table tbody tr td:nth-child(3)").all_inner_texts()
    assert moduleCells and all(value == "ChildLockController" for value in moduleCells)


@pytest.mark.e2e
def test_tcFr02703_testDetailSearchDefaultsToCurrentBuild(page, liveServerUrl):
    """!
    @brief TC-FR-027-03: searching from a test-detail page (build 10) opens
           the search results page with the build filter defaulted to 10
           (FR-027).
    """
    page.goto(liveServerUrl + "/builds/10")
    page.locator(".tests-table tbody tr").first.locator("a").click()

    page.locator(".search-form input[name='q']").fill("EvaluateLockRequest")
    page.locator(".search-form button[type='submit']").click()

    page.wait_for_url("**/search*")
    expect(page.locator("#build-filter")).to_have_value("10")


@pytest.mark.e2e
def test_tcFr02801_moduleFilterOptionsAreOnlyTheTenRealModules(page, liveServerUrl):
    """!
    @brief TC-FR-028-01 (negative): the module filter dropdown lists only the
           10 modules that actually exist in the data -- no fixed/fake
           entries like "NoSuchModuleXYZ" (FR-028).
    """
    page.goto(liveServerUrl + "/search")
    optionValues = page.locator("#module-filter option").evaluate_all("options => options.map(o => o.value)")

    assert "NoSuchModuleXYZ" not in optionValues
    realModuleOptions = [value for value in optionValues if value]  # drop the "" (전체) placeholder
    assert len(realModuleOptions) == 10


@pytest.mark.e2e
def test_tcFr02802_functionFilterOptionsScopedToCurrentModule(page, liveServerUrl):
    """!
    @brief TC-FR-028-02: on ChildLockController's module-detail page, the
           function/suite filter only offers values that actually occur
           within that module -- no other module's function names (FR-028).
    """
    page.goto(liveServerUrl + "/builds/10/modules/ChildLockController")
    functionOptions = {value for value in page.locator("#function-or-suite-filter option").all_inner_texts() if value}

    page.goto(liveServerUrl + "/builds/10/modules/DiagnosticManager")
    diagnosticOnlyOptions = {
        value for value in page.locator("#function-or-suite-filter option").all_inner_texts() if value
    } - functionOptions

    assert functionOptions
    assert diagnosticOnlyOptions  # DiagnosticManager has functions ChildLockController does not


@pytest.mark.e2e
def test_tcFr02901_combinedBuildModuleFailedOnlyFilterReturnsExactThree(page, liveServerUrl):
    """!
    @brief TC-FR-029-01: combining buildId=10, module=ChildLockController and
           failedOnly=true returns exactly 3 rows (§7.1, FR-029).
    """
    page.goto(liveServerUrl + "/search?buildId=10&module=ChildLockController&failedOnly=true")
    expect(page.locator(".tests-table tbody tr")).to_have_count(3)


@pytest.mark.e2e
def test_tcFr02902_resetLinkRestoresFullBuildResultCount(page, liveServerUrl):
    """!
    @brief TC-FR-029-02: from a filtered search, following the reset link
           restores build 10's full 1,200-row list (FR-029).
    """
    page.goto(liveServerUrl + "/search?buildId=10&module=ChildLockController&failedOnly=true")
    page.locator("a.reset-link").click()

    page.goto(liveServerUrl + "/builds/10")
    expect(page.locator("#build-tests-heading")).to_contain_text("1200건")


## Maps a FR-030 sort key to the 1-based tests-table column its values sort by.
_sortKeyToColumn = {"status": 1, "module": 2, "functionOrSuite": 3, "testName": 5, "duration": 6}


def _columnValues(page, columnIndex):
    """!
    @brief Read one column's cell text across every visible tests-table row.
    @param page Playwright page with a list route already loaded.
    @param columnIndex 1-based <td> column index.
    @return List of that column's cell texts, in row order.
    """
    return page.locator(f".tests-table tbody tr td:nth-child({columnIndex})").all_inner_texts()


@pytest.mark.e2e
def test_tcFr03001_allFiveSortKeysReorderTheList(page, liveServerUrl):
    """!
    @brief TC-FR-030-01: each of the 5 sort keys (status/module/
           functionOrSuite/testName/duration) reorders build 10's list
           according to that key -- verified by checking the resulting
           column is itself sorted, since this dataset's unsorted discovery
           order already happens to be module-ascending (files are
           discovered in alphabetical filename order), so a plain
           not-equal-to-default check would wrongly fail sort=module
           specifically (FR-030).
    """
    for sortKey, columnIndex in _sortKeyToColumn.items():
        page.goto(f"{liveServerUrl}/builds/10?sort={sortKey}")
        columnValues = _columnValues(page, columnIndex)

        if sortKey == "duration":
            columnValues = [float(value.rstrip("s")) for value in columnValues]
        assert columnValues == sorted(columnValues), f"sort={sortKey} did not order column {columnIndex}"


@pytest.mark.e2e
def test_tcFr03002_failedOnlyDefaultSortIsModuleThenFunctionThenTestName(page, liveServerUrl):
    """!
    @brief TC-FR-030-02: with failedOnly=true and no explicit sort, the 24
           rows are ordered by module, then function/suite, then test name
           ascending (FR-030).
    """
    page.goto(liveServerUrl + "/builds/10?failedOnly=true")
    rows = page.locator(".tests-table tbody tr")

    modules = rows.locator("td:nth-child(2)").all_inner_texts()
    functions = rows.locator("td:nth-child(3)").all_inner_texts()
    testNames = rows.locator("td:nth-child(5)").all_inner_texts()
    actualTuples = list(zip(modules, functions, testNames))

    assert actualTuples == sorted(actualTuples)


@pytest.mark.e2e
def test_tcFr03003_reloadingSameUrlKeepsIdenticalOrder(page, liveServerUrl):
    """!
    @brief TC-FR-030-03: reloading the exact same failedOnly URL twice
           returns rows in the identical order both times (stable sort,
           FR-030).
    """
    url = liveServerUrl + "/builds/10?failedOnly=true"
    page.goto(url)
    firstOrder = page.locator(".tests-table tbody tr td:nth-child(5)").all_inner_texts()

    page.goto(url)
    secondOrder = page.locator(".tests-table tbody tr td:nth-child(5)").all_inner_texts()

    assert firstOrder == secondOrder


@pytest.mark.e2e
def test_tcFr03101_defaultPageSizeGivesTwentyFourPages(page, liveServerUrl):
    """!
    @brief TC-FR-031-01 (boundary): with no pageSize given, build 10's 1,200
           results paginate at the default 50/page, giving 24 total pages
           (FR-031).
    """
    page.goto(liveServerUrl + "/builds/10")
    paginationText = page.locator(".pagination-range").inner_text()
    assert "24" in paginationText.split("페이지")[1]


@pytest.mark.e2e
def test_tcFr03102_pageSizeTwentyFiveAndOneHundredRecomputeTotalPages(page, liveServerUrl):
    """!
    @brief TC-FR-031-02: switching pageSize to 25 gives 48 total pages, and
           to 100 gives 12 total pages (1200/pageSize, FR-031).
    """
    page.goto(liveServerUrl + "/builds/10?pageSize=25")
    assert "48" in page.locator(".pagination-range").inner_text().split("페이지")[1]

    page.goto(liveServerUrl + "/builds/10?pageSize=100")
    assert "12" in page.locator(".pagination-range").inner_text().split("페이지")[1]


@pytest.mark.e2e
def test_tcFr03103_currentRangeAndTotalShownOnPageTwo(page, liveServerUrl):
    """!
    @brief TC-FR-031-03: page 2 at pageSize=50 shows the "51-100 / 전체
           1200건" style range-and-total text (FR-031).
    """
    page.goto(liveServerUrl + "/builds/10?page=2&pageSize=50")
    rangeText = page.locator(".pagination-range").inner_text()

    assert "51" in rangeText and "100" in rangeText
    assert "1200" in rangeText


## --- UX enhancement: query-controls auto-submit on checkbox/select change ---
##
## Not transcribed from TestCase_Template.xlsx (no TC_ID) -- these cover a UX
## fix discovered via manual/browser exploration: the shared query-controls
## form (_list_controls.html) only reflected a changed checkbox or <select>
## after the user separately clicked "적용". Real users (unlike most of the
## tests above, which navigate straight to a query-string URL) toggle the
## control and expect the list to react immediately. These tests drive the
## actual controls with page.check()/select_option() -- never page.goto()
## with a pre-built query string -- and assert the list updates without any
## "적용" click.


@pytest.mark.e2e
def test_uxAutoSubmit01_checkingFailedOnlyCheckboxNarrowsListWithoutApplyClick(page, liveServerUrl):
    """!
    @brief Checking the "실패 테스트만" checkbox alone (no "적용" click)
           immediately narrows build 10's list to the 24 FAILED rows.
    """
    page.goto(liveServerUrl + "/builds/10")
    expect(page.locator(".tests-table tbody tr")).to_have_count(50)  # default page size

    page.locator(".query-controls input[name='failedOnly']").check()

    expect(page.locator(".tests-table tbody tr")).to_have_count(24)
    statuses = page.locator(".tests-table tbody tr td:first-child").all_inner_texts()
    assert all(status == "FAILED" for status in statuses)


@pytest.mark.e2e
def test_uxAutoSubmit02_choosingStatusFilterNarrowsListWithoutApplyClick(page, liveServerUrl):
    """!
    @brief Selecting "FAILED" from the status <select> alone (no "적용"
           click) immediately narrows build 10's list to only FAILED rows.
    """
    page.goto(liveServerUrl + "/builds/10")

    page.locator("#status-filter").select_option("FAILED")

    page.wait_for_url("**status=FAILED**")
    statuses = page.locator(".tests-table tbody tr td:first-child").all_inner_texts()
    assert statuses and all(status == "FAILED" for status in statuses)


@pytest.mark.e2e
def test_uxAutoSubmit03_textSearchBoxStillRequiresEnterOrButton(page, liveServerUrl):
    """!
    @brief Typing into the free-text search box must NOT auto-submit --
           only Enter or the "적용" button should trigger a navigation, so
           the URL stays unchanged while the user is still typing.
    """
    page.goto(liveServerUrl + "/search")
    urlBeforeTyping = page.url

    page.locator(".query-controls input[name='q']").fill("EvaluateLockRequest")

    assert page.url == urlBeforeTyping

    page.locator(".query-controls input[name='q']").press("Enter")
    page.wait_for_url("**q=EvaluateLockRequest**")


@pytest.mark.e2e
def test_uxControls01_realCheckboxAndSelectCombineToExactThreeRows(page, liveServerUrl):
    """!
    @brief Real-control equivalent of TC-FR-029-01: on /search, choosing
           buildId=10 and module=ChildLockController from the <select>
           elements and checking "실패 테스트만" (no page.goto query string,
           no "적용" click) narrows the list to exactly 3 rows.
    """
    page.goto(liveServerUrl + "/search")

    page.locator("#build-filter").select_option("10")
    page.locator("#module-filter").select_option("ChildLockController")
    page.locator(".query-controls input[name='failedOnly']").check()

    expect(page.locator(".tests-table tbody tr")).to_have_count(3)


@pytest.mark.e2e
def test_uxControls02_realSortSelectReordersListByStatus(page, liveServerUrl):
    """!
    @brief Real-control equivalent of TC-FR-030-01 for the status sort key:
           choosing "상태" from the sort <select> on /builds/10 (no
           page.goto query string) reorders the table by status ascending.
    """
    page.goto(liveServerUrl + "/builds/10")

    page.locator("#sort-select").select_option("status")

    page.wait_for_url("**sort=status**")
    statuses = page.locator(".tests-table tbody tr td:first-child").all_inner_texts()
    assert statuses == sorted(statuses)


@pytest.mark.e2e
def test_uxControls03_realPageSizeSelectRecomputesTotalPages(page, liveServerUrl):
    """!
    @brief Real-control equivalent of TC-FR-031-02: choosing "100" from the
           page-size <select> on /builds/10 (no page.goto query string)
           recomputes the pagination to 12 total pages.
    """
    page.goto(liveServerUrl + "/builds/10")

    page.locator("#page-size-select").select_option("100")

    page.wait_for_url("**pageSize=100**")
    assert "12" in page.locator(".pagination-range").inner_text().split("페이지")[1]
