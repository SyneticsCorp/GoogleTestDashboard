"""!
@file test_e2e_fr018_021_build_module_detail.py
@brief Browser E2E tests transcribed from TestCase_Template.xlsx for
       TS-FR-018 (build summary + prev/next nav), TS-FR-019 (build's full
       test list), TS-FR-020 (module summary) and TS-FR-021 (module test
       list + function/suite filter).

Covers TC-FR-018-01/02/03/04, TC-FR-019-01, TC-FR-020-01/02,
TC-FR-021-01/02 (none tagged "(제안)").
"""
import pytest
from playwright.sync_api import expect

## §7.1's 10 module names, in the order Requirements.md/CLAUDE.md list them.
_allTenModules = [
    "ChildLockController",
    "CommunicationGateway",
    "DiagnosticManager",
    "DoorStateManager",
    "LockActuator",
    "PersistenceManager",
    "SpeedInterlock",
    "StateConsistencyMonitor",
    "SwitchInput",
    "VehicleSignalAdapter",
]


@pytest.mark.e2e
def test_tcFr01801_buildTenSummaryShowsAcceptanceMetrics(page, liveServerUrl):
    """!
    @brief TC-FR-018-01: build 10's detail page shows total 1200/failed 24/
           failure rate 2.0% and 10 module rows in its own module table
           (FR-018).
    """
    page.goto(liveServerUrl + "/builds/10")

    expect(page.locator(".stat-tile", has_text="전체")).to_contain_text("1200")
    expect(page.locator(".stat-tile.stat-tile--failed")).to_contain_text("24")
    expect(page.locator(".stat-tile", has_text="실패율")).to_contain_text("2.0%")
    expect(page.locator(".module-table tbody tr")).to_have_count(10)


@pytest.mark.e2e
def test_tcFr01802_firstBuildHasNoPreviousLink(page, liveServerUrl):
    """!
    @brief TC-FR-018-02 (boundary): build 01 has no "이전 빌드" link -- only
           the disabled placeholder span (FR-018).
    """
    page.goto(liveServerUrl + "/builds/01")

    expect(page.locator("a.build-nav-link", has_text="이전 빌드")).to_have_count(0)
    expect(page.locator("span.build-nav-link--disabled", has_text="이전 빌드")).to_be_visible()


@pytest.mark.e2e
def test_tcFr01803_lastBuildHasNoNextLink(page, liveServerUrl):
    """!
    @brief TC-FR-018-03 (boundary): build 10 has no "다음 빌드" link -- only
           the disabled placeholder span (FR-018).
    """
    page.goto(liveServerUrl + "/builds/10")

    expect(page.locator("a.build-nav-link", has_text="다음 빌드")).to_have_count(0)
    expect(page.locator("span.build-nav-link--disabled", has_text="다음 빌드")).to_be_visible()


@pytest.mark.e2e
def test_tcFr01804_middleBuildHasBothLinksWorking(page, liveServerUrl):
    """!
    @brief TC-FR-018-04: build 05 has both a working "이전 빌드"(→04) and
           "다음 빌드"(→06) link (FR-018).
    """
    page.goto(liveServerUrl + "/builds/05")

    prevLink = page.locator("a.build-nav-link", has_text="이전 빌드")
    nextLink = page.locator("a.build-nav-link", has_text="다음 빌드")
    expect(prevLink).to_be_visible()
    expect(nextLink).to_be_visible()

    nextLink.click()
    page.wait_for_url("**/builds/06")
    page.locator("a.build-nav-link", has_text="이전 빌드").click()
    page.wait_for_url("**/builds/05")


@pytest.mark.e2e
def test_tcFr01901_buildTenUnfilteredShowsAllTwelveHundredWithColumns(page, liveServerUrl):
    """!
    @brief TC-FR-019-01: build 10's test list, with no filter applied, shows
           all 1,200 results and each row has status/module/function/suite/
           test name/duration/file:line populated (§7, FR-019).
    """
    page.goto(liveServerUrl + "/builds/10")

    expect(page.locator("#build-tests-heading")).to_contain_text("1200건")
    firstRowCells = page.locator(".tests-table tbody tr").first.locator("td").all_inner_texts()
    assert len(firstRowCells) == 7
    assert all(cell.strip() for cell in firstRowCells[:-1])  # file:line may legitimately be "-"


@pytest.mark.e2e
def test_tcFr02001_allTenModulesShowOneHundredTwentyTotalEach(page, liveServerUrl):
    """!
    @brief TC-FR-020-01: every one of build 10's 10 modules shows total=120
           in its own module-detail summary (§7.1, FR-020).
    """
    for module in _allTenModules:
        page.goto(f"{liveServerUrl}/builds/10/modules/{module}")
        expect(page.locator(".stat-tile", has_text="전체")).to_contain_text("120")


@pytest.mark.e2e
def test_tcFr02002_moduleTrendShowsAllTenBuilds(page, liveServerUrl):
    """!
    @brief TC-FR-020-02: ChildLockController's build-over-build failure-rate
           trend table has one row per build (01~10), each with a value
           (FR-020).
    """
    page.goto(liveServerUrl + "/builds/10/modules/ChildLockController")

    rows = page.locator(".module-trend-table tbody tr")
    expect(rows).to_have_count(10)
    buildIds = rows.locator("td:first-child").all_inner_texts()
    assert buildIds == [f"{i:02d}" for i in range(1, 11)]


@pytest.mark.e2e
def test_tcFr02101_childLockControllerUnfilteredShowsOneHundredTwenty(page, liveServerUrl):
    """!
    @brief TC-FR-021-01: ChildLockController's test list, unfiltered, shows
           120 results scoped to just that module (§7.1, FR-021).
    """
    page.goto(liveServerUrl + "/builds/10/modules/ChildLockController")
    expect(page.locator("#module-tests-heading")).to_contain_text("120건")
    expect(page.locator(".tests-table tbody tr")).to_have_count(50)  # page 1 of the default pageSize=50


@pytest.mark.e2e
def test_tcFr02102_functionOrSuiteFilterNarrowsResults(page, liveServerUrl):
    """!
    @brief TC-FR-021-02: filtering ChildLockController by function/suite
           "EvaluateLockRequest" narrows the 120-row list to just that
           function's rows, all matching (FR-021).
    """
    page.goto(liveServerUrl + "/builds/10/modules/ChildLockController?functionOrSuite=EvaluateLockRequest")

    heading = page.locator("#module-tests-heading").inner_text()
    matchCount = int(heading.split("(")[1].split("건")[0])
    assert 0 < matchCount < 120

    functionCells = page.locator(".tests-table tbody tr td:nth-child(2)").all_inner_texts()
    assert all(value == "EvaluateLockRequest" for value in functionCells)
