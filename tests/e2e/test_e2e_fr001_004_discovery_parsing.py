"""!
@file test_e2e_fr001_004_discovery_parsing.py
@brief Browser E2E tests transcribed from TestCase_Template.xlsx for
       TS-FR-001~TS-FR-004 (FR-001 results-path resolution, FR-002 build
       discovery/sort, FR-003 XML discovery/dedup, FR-004 parsing accuracy).

Covers TC-FR-001-01/02, TC-FR-002-01, TC-FR-003-01, TC-FR-004-01/02. Every
other TC under these TS_IDs in the xlsx is tagged "(제안: ... 필요)" and
requires synthetic data outside this run's scope (already covered by
tests/integration and tests/unit).
"""
import pytest
from playwright.sync_api import expect


@pytest.mark.e2e
def test_tcFr00101_defaultPathFindsTenBuilds(page, liveServerUrl):
    """!
    @brief TC-FR-001-01: with no results path configured, the app defaults to
           ./GoogleTestResults and finds all 10 builds (FR-001).
    """
    page.goto(liveServerUrl + "/")

    expect(page.locator(".build-history-table tbody tr")).to_have_count(10)
    expect(page.locator("#latest-summary-heading")).to_contain_text("10")


@pytest.mark.e2e
def test_tcFr00102_missingResultsPathShowsErrorNotStackTrace(liveServerUrl, page):
    """!
    @brief TC-FR-001-02: a non-existent results path fails to start with a
           ResultsPathError carrying the reason and the offending path,
           instead of the app silently rendering a blank page (FR-001).

    createApp() raises synchronously when the path does not exist, so this
    is exercised directly rather than through the browser (there is no route
    that lets a live request reconfigure the path at runtime).
    """
    from gtestdash.config import ResultsPathError
    from gtestdash.web.app import createApp

    badPath = r"D:\GoogleTestExample\NotExist_20260902"
    with pytest.raises(ResultsPathError) as excInfo:
        createApp(badPath)

    assert badPath in str(excInfo.value)
    assert excInfo.value.reason


@pytest.mark.e2e
def test_tcFr00201_tenBuildsIdentifiedInNumericOrder(page, liveServerUrl):
    """!
    @brief TC-FR-002-01: the build history list identifies all 10 build
           folders and orders them numerically (09 before 10, not "1" before
           "10" as a string sort would) (FR-002).
    """
    page.goto(liveServerUrl + "/")

    buildIdCells = page.locator(".build-history-table tbody tr td:first-child")
    expect(buildIdCells).to_have_count(10)
    displayedIds = buildIdCells.all_inner_texts()
    assert displayedIds == ["10", "09", "08", "07", "06", "05", "04", "03", "02", "01"]


@pytest.mark.e2e
def test_tcFr00301_tenModulesPerBuildOneHundredXmlTotal(page, liveServerUrl):
    """!
    @brief TC-FR-003-01: build 10 has exactly 10 module rows (one per XML
           file), and every other build has the same count, for 100 XML
           files identified across the dataset (FR-003).
    """
    page.goto(liveServerUrl + "/builds/10")
    expect(page.locator(".module-table tbody tr")).to_have_count(10)

    for buildId in range(1, 11):
        page.goto(f"{liveServerUrl}/builds/{buildId:02d}")
        expect(page.locator(".module-table tbody tr")).to_have_count(10)


@pytest.mark.e2e
def test_tcFr00401_twelveThousandRecordsAcrossTenBuilds(page, liveServerUrl):
    """!
    @brief TC-FR-004-01: each build's test list totals 1,200 records, and the
           10 builds sum to 12,000 normalized records (FR-004, §8-2).
    """
    grandTotal = 0
    for buildId in range(1, 11):
        page.goto(f"{liveServerUrl}/builds/{buildId:02d}")
        heading = page.locator("#build-tests-heading").inner_text()
        countInHeading = int(heading.split("(")[1].split("건")[0].replace(",", ""))
        assert countInHeading == 1200
        grandTotal += countInHeading

    assert grandTotal == 12000


@pytest.mark.e2e
def test_tcFr00402_passedTestWithoutFailureElementRendersDetail(page, liveServerUrl):
    """!
    @brief TC-FR-004-02: a <testcase> with no <failure> child still becomes a
           normalized PASSED record and its detail page renders without
           error (FR-004, links to FR-024).
    """
    page.goto(liveServerUrl + "/builds/10")
    passedRow = page.locator("tr.test-row--passed").first
    passedRow.locator("a").click()

    expect(page.locator("#test-summary-heading")).to_be_visible()
    expect(page.locator(".stat-tile", has_text="상태")).to_contain_text("PASSED")
