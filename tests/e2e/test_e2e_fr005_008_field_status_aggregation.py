"""!
@file test_e2e_fr005_008_field_status_aggregation.py
@brief Browser E2E tests transcribed from TestCase_Template.xlsx for
       TS-FR-005 (module/function fallback), TS-FR-006 (status priority),
       TS-FR-007 (aggregate calculation) and TS-FR-008 (declared-vs-computed
       mismatch warnings).

Covers TC-FR-005-06, TC-FR-006-05/06/13/14/15, TC-FR-007-01/02/03,
TC-FR-008-01. Every other TC under these TS_IDs is tagged "(제안: ... 필요)"
and requires synthetic multi-evidence XML outside this run's scope (already
covered by tests/unit/test_status_resolver.py and
tests/unit/test_field_resolver.py). TC-FR-006-06/13/15 (DISABLED/ERROR/
SKIPPED) have no naturally-occurring example in the real dataset (it only
ever produces PASSED/FAILED), so they reuse the same
status_priority_conflict.xml fixture the unit tests already rely on, via the
statusPriorityServerUrl fixture (see conftest.py).
"""
import pytest
from playwright.sync_api import expect


@pytest.mark.e2e
def test_tcFr00506_modulePropertyAndFunctionPropertyBothUsed(page, liveServerUrl):
    """!
    @brief TC-FR-005-06 (baseline PICT combo #6): when both a module property
           and a tested_function property are present, both take precedence
           over their classname/name-pattern fallbacks (FR-005). Every real
           record in the dataset is generated this way, so any test detail
           page demonstrates it.
    """
    page.goto(liveServerUrl + "/builds/10/modules/ChildLockController")
    page.locator(".tests-table tbody tr").first.locator("a").click()

    expect(page.locator(".stat-tile", has_text="모듈")).to_contain_text("ChildLockController")
    functionTile = page.locator(".stat-tile", has_text="함수")
    expect(functionTile).to_be_visible()
    functionValue = functionTile.locator("dd").inner_text()
    assert functionValue and functionValue != "-"


def _gotoStatusCase(page, baseUrl, testName):
    """!
    @brief Navigate to one status_priority_conflict.xml testcase's detail page.
    @param page Playwright page.
    @param baseUrl statusPriorityServerUrl's base URL.
    @param testName The <testcase name="..."> to look up within build 99.
    """
    page.goto(f"{baseUrl}/builds/99/modules/StatusPriorityFixture")
    page.locator(".tests-table tbody tr", has_text=testName).locator("a").click()


@pytest.mark.e2e
def test_tcFr00605_noEvidenceResolvesToPassed(page, statusPriorityServerUrl):
    """!
    @brief TC-FR-006-05 (PICT #5): no failure/error/skipped/disabled marker
           resolves to PASSED (FR-006).
    """
    _gotoStatusCase(page, statusPriorityServerUrl, "PlainPass")
    expect(page.locator(".stat-tile", has_text="상태")).to_contain_text("PASSED")


@pytest.mark.e2e
def test_tcFr00606_onlyDisabledMarkerResolvesToDisabled(page, statusPriorityServerUrl):
    """!
    @brief TC-FR-006-06 (PICT #6): status="notrun" alone resolves to DISABLED
           (FR-006).
    """
    _gotoStatusCase(page, statusPriorityServerUrl, "OnlyDisabledStatusAttr")
    expect(page.locator(".stat-tile", has_text="상태")).to_contain_text("DISABLED")


@pytest.mark.e2e
def test_tcFr00613_onlyErrorMarkerResolvesToError(page, statusPriorityServerUrl):
    """!
    @brief TC-FR-006-13 (PICT #13): an <error> element alone resolves to
           ERROR (FR-006).
    """
    _gotoStatusCase(page, statusPriorityServerUrl, "OnlyError")
    expect(page.locator(".stat-tile", has_text="상태")).to_contain_text("ERROR")


@pytest.mark.e2e
def test_tcFr00614_onlyFailureMarkerResolvesToFailed(page, statusPriorityServerUrl):
    """!
    @brief TC-FR-006-14 (PICT #14): a <failure> element alone resolves to
           FAILED (FR-006).
    """
    _gotoStatusCase(page, statusPriorityServerUrl, "OnlyFailure")
    expect(page.locator(".stat-tile", has_text="상태")).to_contain_text("FAILED")


@pytest.mark.e2e
def test_tcFr00615_onlySkippedMarkerResolvesToSkipped(page, statusPriorityServerUrl):
    """!
    @brief TC-FR-006-15 (PICT #15): a <skipped> element alone resolves to
           SKIPPED (FR-006).
    """
    _gotoStatusCase(page, statusPriorityServerUrl, "OnlySkipped")
    expect(page.locator(".stat-tile", has_text="상태")).to_contain_text("SKIPPED")


@pytest.mark.e2e
def test_tcFr00701_tenBuildFailureRatesMatchAcceptanceValues(page, liveServerUrl):
    """!
    @brief TC-FR-007-01: builds 01~10 show failure rates 8/4/9/6/3/7/5/10/4/2%
           in both the build-history table and each build's own detail page
           (§7 acceptance data, FR-007).
    """
    expectedRates = ["8.0%", "4.0%", "9.0%", "6.0%", "3.0%", "7.0%", "5.0%", "10.0%", "4.0%", "2.0%"]

    page.goto(liveServerUrl + "/")
    historyRates = page.locator(".build-history-table tbody tr td:nth-child(6)").all_inner_texts()
    assert historyRates == list(reversed(expectedRates))

    for buildId, expectedRate in zip(range(1, 11), expectedRates):
        page.goto(f"{liveServerUrl}/builds/{buildId:02d}")
        expect(page.locator(".stat-grid").locator(".stat-tile", has_text="실패율")).to_contain_text(expectedRate)


@pytest.mark.e2e
def test_tcFr00702_failureRateFormulaOnBuildTen(page, liveServerUrl):
    """!
    @brief TC-FR-007-02: build 10's failure rate is computed as
           failed/total*100 = 24/1200*100 = 2.0% (FR-007, matches FR-010).
    """
    page.goto(liveServerUrl + "/builds/10")

    expect(page.locator(".stat-tile", has_text="전체")).to_contain_text("1200")
    expect(page.locator(".stat-tile.stat-tile--failed")).to_contain_text("24")
    expect(page.locator(".stat-tile", has_text="실패율")).to_contain_text("2.0%")


@pytest.mark.e2e
def test_tcFr00703_zeroMatchesShowsNotApplicableNotZeroPercent(page, liveServerUrl):
    """!
    @brief TC-FR-007-03 (boundary): a query matching zero tests must not
           render a misleading 0% failure rate anywhere on the page; there is
           no total-count denominator to divide by (FR-007, links to FR-036).
    """
    page.goto(liveServerUrl + "/search?q=zzz_no_such_test_20260902")

    expect(page.locator("#search-results-heading")).to_contain_text("0건")
    assert "0.0%" not in page.locator("main").inner_text()


@pytest.mark.e2e
def test_tcFr00801_matchingDeclaredCountsShowNoMismatchWarning(page, liveServerUrl):
    """!
    @brief TC-FR-008-01: a build whose XML declared counts match the computed
           counts (the real dataset, per generation_manifest.json) shows no
           mismatch warning banner (FR-008).
    """
    page.goto(liveServerUrl + "/builds/10")
    expect(page.locator(".warning-banner")).to_have_count(0)
