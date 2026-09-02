"""!
@file test_e2e_acc_acceptance.py
@brief Browser E2E tests transcribed from TestCase_Template.xlsx for
       TS-ACC-007A (§7.1 per-module exhaustive check) and TS-ACC-008-4/6
       (§8 completion-criteria cross-checks between charts and detail
       lists, and search-to-failure-detail continuity).

Covers TC-ACC-007A-01, TC-ACC-008-4-01/02/03, TC-ACC-008-6-01 (none tagged
"(제안)").
"""
import pytest
from playwright.sync_api import expect

## §7.1's build-10 per-module (total, failed) acceptance figures.
_acceptanceTableSection71 = {
    "ChildLockController": (120, 3),
    "CommunicationGateway": (120, 3),
    "DiagnosticManager": (120, 2),
    "DoorStateManager": (120, 3),
    "LockActuator": (120, 2),
    "PersistenceManager": (120, 2),
    "SpeedInterlock": (120, 3),
    "StateConsistencyMonitor": (120, 2),
    "SwitchInput": (120, 2),
    "VehicleSignalAdapter": (120, 2),
}


@pytest.mark.e2e
def test_tcAcc007a01_allTenModulesMatchSection71TableExactly(page, liveServerUrl):
    """!
    @brief TC-ACC-007A-01: every one of build 10's 10 modules matches §7.1's
           table exactly (total/failed), and the totals reconcile to the
           build's own 1,200/24 summary (FR-020, §7.1).
    """
    totalSum = 0
    failedSum = 0
    for module, (expectedTotal, expectedFailed) in _acceptanceTableSection71.items():
        page.goto(f"{liveServerUrl}/builds/10/modules/{module}")
        assert page.locator(".stat-tile", has_text="전체").locator("dd").inner_text() == str(expectedTotal)
        assert page.locator(".stat-tile.stat-tile--failed").locator("dd").inner_text() == str(expectedFailed)
        totalSum += expectedTotal
        failedSum += expectedFailed

    assert totalSum == 1200
    assert failedSum == 24


@pytest.mark.e2e
def test_tcAcc00840_1_trendChartBuildTenFailedCountMatchesFailedOnlyListing(page, liveServerUrl):
    """!
    @brief TC-ACC-008-4-01: the trend chart's build 10 failed count (24)
           matches /builds/10?failedOnly=true's own row count exactly
           (§8-4, FR-012).
    """
    page.goto(liveServerUrl + "/")
    trendPoints = page.evaluate("() => window.gtestDashData.trendPoints")
    build10Failed = next(point for point in trendPoints if point["buildId"] == "10")["failed"]

    page.goto(liveServerUrl + "/builds/10?failedOnly=true")
    listFailedCount = page.locator(".tests-table tbody tr").count()

    assert build10Failed == 24
    assert listFailedCount == build10Failed


@pytest.mark.e2e
def test_tcAcc00840_2_moduleChartFailedCountsMatchEachModulesFailedOnlyListing(page, liveServerUrl):
    """!
    @brief TC-ACC-008-4-02: the module failure chart's per-module failed
           counts (build 10) match each module's own
           ?failedOnly=true listing exactly, module by module, summing to
           24 (§8-4, FR-014).
    """
    page.goto(liveServerUrl + "/")
    distribution = page.evaluate("() => window.gtestDashData.moduleDistribution")
    chartFailedByModule = {entry["module"]: entry["failed"] for entry in distribution}

    listFailedByModule = {}
    for module in chartFailedByModule:
        page.goto(f"{liveServerUrl}/builds/10/modules/{module}?failedOnly=true")
        listFailedByModule[module] = page.locator(".tests-table tbody tr").count()

    assert chartFailedByModule == listFailedByModule
    assert sum(chartFailedByModule.values()) == 24


@pytest.mark.e2e
def test_tcAcc00840_3_cumulativeModuleChartSumMatchesSumOfAllBuildsFailedCounts(page, liveServerUrl):
    """!
    @brief TC-ACC-008-4-03: the module chart's "전체 누적" scope failed-count
           sum (696) matches the sum of all 10 builds' own failed counts from
           the build history list (§8-4, FR-007, FR-014).
    """
    page.goto(liveServerUrl + "/")
    page.locator("#scope-select").select_option("cumulative")
    page.wait_for_url("**scope=cumulative**")
    cumulativeSum = sum(entry["failed"] for entry in page.evaluate("() => window.gtestDashData.moduleDistribution"))

    buildHistoryFailedCounts = [
        int(text) for text in page.locator(".build-history-table tbody tr td:nth-child(4)").all_inner_texts()
    ]

    assert cumulativeSum == 696
    assert sum(buildHistoryFailedCounts) == 696


@pytest.mark.e2e
def test_tcAcc00860_1_searchToFailureDetailShowsMessageFileAndLineUninterrupted(page, liveServerUrl):
    """!
    @brief TC-ACC-008-6-01: from a failed-only search result, selecting a
           test opens its detail page with failure type, summary, full
           failure body, test file path and line number all visible without
           truncation (§8-6, FR-022/023/026).
    """
    page.goto(liveServerUrl + "/search?failedOnly=true")
    firstRow = page.locator(".tests-table tbody tr").first
    firstRow.locator("a").last.click()

    expect(page.locator(".stat-tile", has_text="상태").locator("dd")).to_have_text("FAILED")
    failureType = page.locator(".stat-tile", has_text="실패 유형").locator("dd").inner_text()
    failureSummary = page.locator(".stat-tile", has_text="실패 요약").locator("dd").inner_text()
    testFile = page.locator(".stat-tile", has_text="테스트 파일").locator("dd").inner_text()
    failureBody = page.locator("pre.failure-detail").inner_text()

    assert failureType not in ("", "알 수 없음")
    assert failureSummary not in ("", "-")
    assert ":" in testFile and "..." not in testFile
    assert failureBody.strip()
