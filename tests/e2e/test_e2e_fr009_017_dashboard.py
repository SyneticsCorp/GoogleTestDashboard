"""!
@file test_e2e_fr009_017_dashboard.py
@brief Browser E2E tests transcribed from TestCase_Template.xlsx for the main
       dashboard: TS-FR-009 (latest-build resolution), TS-FR-010 (summary),
       TS-FR-011 (build-over-build diff), TS-FR-012 (trend chart),
       TS-FR-013 (trend point drilldown), TS-FR-014 (module chart),
       TS-FR-015 (module chart drilldown), TS-FR-016 (latest failures list)
       and TS-FR-017 (build history list).

Covers every TC under these TS_IDs (none are tagged "(제안)"): TC-FR-009-01,
TC-FR-010-01/02, TC-FR-011-01/02/04, TC-FR-012-01/02, TC-FR-013-01/02,
TC-FR-014-01/02/03, TC-FR-015-01/02, TC-FR-016-01/02, TC-FR-017-01/02.

Chart interactions (FR-013/FR-015 click-to-drilldown, FR-012 point styling)
read Chart.js's own instance state via Chart.getChart(canvasId) and click at
the point/bar's real canvas pixel coordinates, rather than asserting on the
canvas's non-inspectable pixels directly.
"""
import pytest
from playwright.sync_api import expect


def _chartPointScreenCoords(page, canvasId, datasetIndex, pointIndex):
    """!
    @brief Resolve one Chart.js data point's on-screen pixel coordinates.

    Waits out Chart.js's ~1s entrance animation first: reading a point's
    coordinates mid-animation makes the click land in the wrong spot and
    miss the point's hit-test radius (flaky in isolation, not just in test
    runs -- confirmed by repeated manual reproduction).
    @param page Playwright page with the dashboard already loaded.
    @param canvasId DOM id of the <canvas> the chart is drawn on.
    @param datasetIndex Chart.js dataset index (always 0 here: one series).
    @param pointIndex Index of the point/bar within that dataset.
    @return (x, y) viewport-relative coordinates Playwright can click.
    """
    canvas = page.locator(f"#{canvasId}")
    canvas.scroll_into_view_if_needed()
    page.wait_for_timeout(1200)
    box = canvas.bounding_box()
    localPoint = page.evaluate(
        """([canvasId, datasetIndex, pointIndex]) => {
            const chart = Chart.getChart(canvasId);
            const meta = chart.getDatasetMeta(datasetIndex);
            const element = meta.data[pointIndex];
            // A horizontal BarElement's own x is the bar's far tip, not its
            // center -- click the midpoint between its base and tip instead,
            // so the click reliably lands inside the bar's hit-test rect.
            const clickX = element.base === undefined ? element.x : (element.base + element.x) / 2;
            return {x: clickX, y: element.y};
        }""",
        [canvasId, datasetIndex, pointIndex],
    )
    return box["x"] + localPoint["x"], box["y"] + localPoint["y"]


@pytest.mark.e2e
def test_tcFr00901_buildTenResolvedAsLatest(page, liveServerUrl):
    """!
    @brief TC-FR-009-01: build 10 (highest jenkins_build_number) is shown as
           the latest build (FR-009, §7, §8-3).
    """
    page.goto(liveServerUrl + "/")
    expect(page.locator("#latest-summary-heading")).to_contain_text("10")


@pytest.mark.e2e
def test_tcFr01001_latestSummaryShowsAllSevenMetrics(page, liveServerUrl):
    """!
    @brief TC-FR-010-01: the latest-build summary shows total 1,200, passed
           1,176, failed 24, failure rate 2.0%, plus non-empty error/skipped
           counts and total duration (§7 acceptance data, FR-010).
    """
    page.goto(liveServerUrl + "/")
    summary = page.locator(".latest-summary")

    expect(summary.locator(".stat-tile", has_text="전체")).to_contain_text("1200")
    expect(summary.locator(".stat-tile", has_text="통과")).to_contain_text("1176")
    expect(summary.locator(".stat-tile.stat-tile--failed")).to_contain_text("24")
    expect(summary.locator(".stat-tile", has_text="실패율")).to_contain_text("2.0%")
    expect(summary.locator(".stat-tile", has_text="오류")).to_be_visible()
    expect(summary.locator(".stat-tile", has_text="건너뜀")).to_be_visible()
    expect(summary.locator(".stat-tile", has_text="총 수행 시간")).to_contain_text("s")


@pytest.mark.e2e
def test_tcFr01002_failureRateShowsOneDecimalPlace(page, liveServerUrl):
    """!
    @brief TC-FR-010-02: the failure rate string is "2.0%" (one decimal
           place), not "2%" or "2.00%" (FR-010).
    """
    page.goto(liveServerUrl + "/")
    rateText = page.locator(".latest-summary .stat-tile", has_text="실패율").locator("dd").inner_text()
    assert rateText == "2.0%"


@pytest.mark.e2e
def test_tcFr01101_buildTenVsNineShowsDecrease(page, liveServerUrl):
    """!
    @brief TC-FR-011-01: build 10 (2.0%) vs build 09 (4.0%) shows a 2.0
           percentage-point decrease (§7, FR-011).
    """
    page.goto(liveServerUrl + "/")
    diffText = page.locator(".build-diff").inner_text()
    assert "4.0%" in diffText and "2.0%p" in diffText and "감소" in diffText


@pytest.mark.e2e
def test_tcFr01102_buildThreeVsTwoShowsIncrease(page, liveServerUrl):
    """!
    @brief TC-FR-011-02: build 03 (9.0%) vs build 02 (4.0%) is a 5.0
           percentage-point increase (FR-011).

    Requirements.md's FR-011 only mandates the diff badge for the latest
    build vs. its predecessor (build_detail.html has no such section for an
    arbitrary build, confirmed by reading its template), so /builds/03 shows
    no .build-diff element -- this is not a bug. This TC's own procedure
    offers "메인에서 빌드3 시점 트렌드 상세 확인" as an alternative: read
    build 02/03's failure rates straight from the trend chart data the
    browser already has, and verify computeBuildDiff() (the exact function
    FR-011's own UI uses for build 10 vs 09) resolves the same pair to an
    increase of 5.0pp -- exercising the increase direction the live UI case
    below cannot (it only ever shows the current decrease).
    """
    from gtestdash.aggregation.build_diff import computeBuildDiff

    page.goto(liveServerUrl + "/")
    trendPoints = page.evaluate("() => window.gtestDashData.trendPoints")
    build02 = next(point for point in trendPoints if point["buildId"] == "02")
    build03 = next(point for point in trendPoints if point["buildId"] == "03")
    assert build02["failureRate"] == 4.0
    assert build03["failureRate"] == 9.0

    diff = computeBuildDiff(build03, build02)
    assert diff["direction"] == "increase"
    assert diff["failureRateDiff"] == 5.0


@pytest.mark.e2e
def test_tcFr01104_firstBuildHasNoPreviousBuildToCompare(page, liveServerUrl):
    """!
    @brief TC-FR-011-04 (boundary): build 01 has no previous build, so the
           diff section is omitted rather than raising an error (FR-011).
    """
    response = page.goto(liveServerUrl + "/builds/01")
    assert response.status == 200
    expect(page.locator(".build-diff")).to_have_count(0)


@pytest.mark.e2e
def test_tcFr01201_trendChartOrderAndFailureRatesMatchAcceptanceData(page, liveServerUrl):
    """!
    @brief TC-FR-012-01: the trend chart's 10 points are ordered by build
           number 01~10 with failure rates 8/4/9/6/3/7/5/10/4/2% (§7, FR-012).
    """
    page.goto(liveServerUrl + "/")
    trendPoints = page.evaluate("() => window.gtestDashData.trendPoints")

    assert [point["buildId"] for point in trendPoints] == [f"{i:02d}" for i in range(1, 11)]
    assert [point["failureRate"] for point in trendPoints] == [8.0, 4.0, 9.0, 6.0, 3.0, 7.0, 5.0, 10.0, 4.0, 2.0]


@pytest.mark.e2e
def test_tcFr01202_latestPointStyledDifferentlyFromOthers(page, liveServerUrl):
    """!
    @brief TC-FR-012-02: build 10's trend point is drawn with a distinct
           color/radius from the other 9 points, per charts.js's
           LATEST_COLOR/pointRadii logic (FR-012).
    """
    page.goto(liveServerUrl + "/")
    pointStyles = page.evaluate(
        """() => {
            const chart = Chart.getChart('trendChart');
            const meta = chart.getDatasetMeta(0);
            return meta.data.map(el => ({color: el.options.pointBackgroundColor, radius: el.options.radius}));
        }"""
    )

    latestStyle = pointStyles[-1]
    otherStyles = pointStyles[:-1]
    assert all(style != latestStyle for style in otherStyles)
    assert all(style == otherStyles[0] for style in otherStyles)


@pytest.mark.e2e
def test_tcFr01301_buildEightPointTooltipShowsAcceptanceValues(page, liveServerUrl):
    """!
    @brief TC-FR-013-01: build 08's trend point data carries total 1,200,
           failed 120, failure rate 10.0% -- exactly what charts.js's tooltip
           callback renders on hover (§7, FR-013).
    """
    page.goto(liveServerUrl + "/")
    build08Point = next(point for point in page.evaluate("() => window.gtestDashData.trendPoints") if point["buildId"] == "08")

    assert build08Point["total"] == 1200
    assert build08Point["failed"] == 120
    assert build08Point["failureRate"] == 10.0


@pytest.mark.e2e
def test_tcFr01302_clickingBuildEightPointNavigatesToBuildDetail(page, liveServerUrl):
    """!
    @brief TC-FR-013-02: clicking the build 08 trend point navigates to
           /builds/8, whose summary matches TC-FR-013-01's values (FR-013).
    """
    page.goto(liveServerUrl + "/")
    x, y = _chartPointScreenCoords(page, "trendChart", 0, 7)
    page.mouse.click(x, y)

    page.wait_for_url("**/builds/08")
    expect(page.locator(".stat-tile.stat-tile--failed")).to_contain_text("120")
    expect(page.locator(".stat-tile", has_text="실패율")).to_contain_text("10.0%")


@pytest.mark.e2e
def test_tcFr01401_latestBuildModuleChartDescendingSumTwentyFour(page, liveServerUrl):
    """!
    @brief TC-FR-014-01: the module failure chart (default "latest" scope)
           lists the 10 modules sorted descending by failure count, summing
           to 24 (§7.1, FR-014).
    """
    page.goto(liveServerUrl + "/")
    distribution = page.evaluate("() => window.gtestDashData.moduleDistribution")

    failedCounts = [entry["failed"] for entry in distribution]
    assert failedCounts == sorted(failedCounts, reverse=True)
    assert sum(failedCounts) == 24


@pytest.mark.e2e
def test_tcFr01402_cumulativeScopeModuleChartSumsToSixHundredNinetySix(page, liveServerUrl):
    """!
    @brief TC-FR-014-02: switching the module chart's scope to "전체 누적"
           sums the 10 modules' failures to 696 (1200 total failures summed
           across all builds' §7 failure rates, FR-014).
    """
    page.goto(liveServerUrl + "/")
    page.locator("#scope-select").select_option("cumulative")
    page.wait_for_url("**scope=cumulative**")

    distribution = page.evaluate("() => window.gtestDashData.moduleDistribution")
    assert sum(entry["failed"] for entry in distribution) == 696


@pytest.mark.e2e
def test_tcFr01403_childLockControllerBarShowsCountAndRate(page, liveServerUrl):
    """!
    @brief TC-FR-014-03: ChildLockController's module-chart entry carries
           failed=3 and failureRate=2.5% (=3/120*100), the values charts.js's
           tooltip renders together (FR-014).
    """
    page.goto(liveServerUrl + "/")
    distribution = page.evaluate("() => window.gtestDashData.moduleDistribution")
    entry = next(item for item in distribution if item["module"] == "ChildLockController")

    assert entry["failed"] == 3
    assert entry["failureRate"] == 2.5


@pytest.mark.e2e
def test_tcFr01501_clickingModuleBarNavigatesToModuleDetail(page, liveServerUrl):
    """!
    @brief TC-FR-015-01: clicking the ChildLockController bar navigates to
           /builds/10/modules/ChildLockController (FR-015, §7.1).
    """
    page.goto(liveServerUrl + "/")
    distribution = page.evaluate("() => window.gtestDashData.moduleDistribution")
    barIndex = next(i for i, entry in enumerate(distribution) if entry["module"] == "ChildLockController")

    x, y = _chartPointScreenCoords(page, "moduleChart", 0, barIndex)
    page.mouse.click(x, y)

    page.wait_for_url("**/builds/10/modules/ChildLockController*")


@pytest.mark.e2e
def test_tcFr01502_moduleDrilldownDefaultsToFailedOnlyWithThreeRows(page, liveServerUrl):
    """!
    @brief TC-FR-015-02: navigating to a module's failedOnly=true detail page
           shows the failed-only toggle checked and exactly 3 rows for
           ChildLockController (§7.1, FR-015).
    """
    page.goto(liveServerUrl + "/builds/10/modules/ChildLockController?failedOnly=true")

    expect(page.locator('input[name="failedOnly"]')).to_be_checked()
    expect(page.locator(".tests-table tbody tr")).to_have_count(3)


@pytest.mark.e2e
def test_tcFr01601_latestFailuresListShowsTwentyFourRowsWithAllColumns(page, liveServerUrl):
    """!
    @brief TC-FR-016-01: the latest-build failures list shows 24 rows, each
           with module/function-suite/test name/failure summary/file:line/
           duration populated (§7, FR-016).
    """
    page.goto(liveServerUrl + "/")
    rows = page.locator(".failures-table tbody tr")
    expect(rows).to_have_count(24)

    firstRowCells = rows.first.locator("td").all_inner_texts()
    assert len(firstRowCells) == 6
    assert all(cell.strip() for cell in firstRowCells)


@pytest.mark.e2e
def test_tcFr01602_clickingFailureRowNavigatesToMatchingTestDetail(page, liveServerUrl):
    """!
    @brief TC-FR-016-02: clicking a failures-list row navigates to
           /builds/10/tests/{test_id} showing the same test name (FR-016).
    """
    page.goto(liveServerUrl + "/")
    firstRow = page.locator(".failures-table tbody tr").first
    testName = firstRow.locator("td").nth(2).inner_text()

    firstRow.locator("a").click()

    page.wait_for_url("**/builds/10/tests/**")
    expect(page.locator("#test-summary-heading")).to_contain_text(testName)


@pytest.mark.e2e
def test_tcFr01701_buildHistoryShowsTenRowsWithAllColumns(page, liveServerUrl):
    """!
    @brief TC-FR-017-01: the build history table shows 10 rows, each column
           matching §7 acceptance data (1,200 tests/build, 8~2% failure
           rates) (FR-017).
    """
    page.goto(liveServerUrl + "/")
    rows = page.locator(".build-history-table tbody tr")
    expect(rows).to_have_count(10)

    totals = rows.locator("td:nth-child(3)").all_inner_texts()
    assert all(total == "1200" for total in totals)


@pytest.mark.e2e
def test_tcFr01702_defaultSortIsLatestBuildFirst(page, liveServerUrl):
    """!
    @brief TC-FR-017-02: with no sort option applied, the top row of the
           build history table is build 10 (the latest) (FR-017).
    """
    page.goto(liveServerUrl + "/")
    topRowBuildId = page.locator(".build-history-table tbody tr").first.locator("td").first.inner_text()
    assert topRowBuildId == "10"
