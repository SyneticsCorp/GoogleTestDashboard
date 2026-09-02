"""!
@file test_e2e_fr022_024_test_detail.py
@brief Browser E2E tests transcribed from TestCase_Template.xlsx for
       TS-FR-022 (test-detail identity fields), TS-FR-023 (failure detail
       rendering) and TS-FR-024 (passed-test "no failure info" state).

Covers TC-FR-022-01, TC-FR-023-01/02, TC-FR-024-01 (none tagged "(제안)").
"""
import pytest
from playwright.sync_api import expect


def _statTileValue(page, label):
    """!
    @brief Read one stat-tile's <dd> value by its <dt> label text.
    @param page Playwright page with a detail page already loaded.
    @param label The stat tile's <dt> label, e.g. "모듈".
    @return The tile's <dd> text content.
    """
    return page.locator(".stat-tile", has_text=label).locator("dd").inner_text()


@pytest.mark.e2e
def test_tcFr02201_testDetailIdentityMatchesSelectedRow(page, liveServerUrl):
    """!
    @brief TC-FR-022-01: every identity field on a test-detail page (build/
           module/function/suite/test name/status/duration/timestamp/test
           file/line/source file) matches the row it was opened from
           (FR-022).
    """
    page.goto(liveServerUrl + "/builds/10")
    firstRow = page.locator(".tests-table tbody tr").first
    rowCells = firstRow.locator("td").all_inner_texts()
    rowStatus, rowModule, rowFunction, rowSuite, rowTestName = rowCells[:5]

    firstRow.locator("a").click()

    expect(page.locator("#test-summary-heading")).to_contain_text(rowTestName)
    assert _statTileValue(page, "빌드") == "10"
    assert _statTileValue(page, "모듈") == rowModule
    assert _statTileValue(page, "함수") == rowFunction
    assert _statTileValue(page, "스위트") == rowSuite
    assert _statTileValue(page, "상태") == rowStatus


@pytest.mark.e2e
def test_tcFr02301_failureDetailShowsTypeSummaryAndFullBodyPreformatted(page, liveServerUrl):
    """!
    @brief TC-FR-023-01: a failing test's detail page shows failure type,
           failure summary, and the full failure body inside a <pre> block
           (preserving line breaks/indentation) (FR-023).
    """
    page.goto(liveServerUrl + "/builds/10?failedOnly=true")
    page.locator(".tests-table tbody tr").first.locator("a").click()

    expect(page.locator("#test-failure-heading")).to_be_visible()
    assert _statTileValue(page, "실패 유형") not in ("", "알 수 없음")
    assert _statTileValue(page, "실패 요약") not in ("", "-")
    failureBody = page.locator("pre.failure-detail")
    expect(failureBody).to_be_visible()
    assert failureBody.inner_text().strip()


@pytest.mark.e2e
def test_tcFr02302_testFileAndLineShownInFullWithoutTruncation(page, liveServerUrl):
    """!
    @brief TC-FR-023-02 (boundary): the test file path is shown in full (no
           ellipsis) with its line number, not omitted (FR-023).
    """
    page.goto(liveServerUrl + "/builds/10?failedOnly=true")
    page.locator(".tests-table tbody tr").first.locator("a").click()

    testFileValue = _statTileValue(page, "테스트 파일")
    assert "..." not in testFileValue
    assert ":" in testFileValue  # "{path}:{line}" shape, e.g. FR-022's file:line column


@pytest.mark.e2e
def test_tcFr02401_passedTestShowsNoFailureInfoWithoutError(page, liveServerUrl):
    """!
    @brief TC-FR-024-01: a PASSED test's detail page shows "실패 정보 없음"
           in place of an empty failure section, and the page itself renders
           without error (FR-024).
    """
    page.goto(liveServerUrl + "/builds/10")
    page.locator("tr.test-row--passed").first.locator("a").click()

    response = page.reload()
    assert response.status == 200
    expect(page.locator(".failure-section")).to_contain_text("실패 정보 없음")
    expect(page.locator("pre.failure-detail")).to_have_count(0)
