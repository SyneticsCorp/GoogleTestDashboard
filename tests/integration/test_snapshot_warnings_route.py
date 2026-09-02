"""!
@file test_snapshot_warnings_route.py
@brief Integration tests for FR-035: a malformed XML is surfaced as a visible
       warning, without breaking the dashboard or the build it belongs to.
"""
import os
import shutil

from _template_capture import capturedTemplateContext as _capturedTemplateContext

from gtestdash.web.app import createApp

## Real, read-only dataset root; copied per-test into tmp_path, never modified directly (CLAUDE.md).
_realResultsRoot = os.path.join(os.path.dirname(__file__), "..", "..", "GoogleTestResults")
## Read-only malformed-XML fixture (unterminated <testsuite>); never modified (CLAUDE.md).
_malformedFixture = os.path.join(
    os.path.dirname(__file__), "..", "fixtures", "edge_cases", "malformed.xml"
)


def _copyResultsTreeWithMalformedFileIn(tmp_path, buildId):
    """!
    @brief Copy the real results tree into tmp_path and inject one malformed
           XML file into the given build folder.
    @param tmp_path pytest tmp_path fixture root.
    @param buildId Build folder name to inject the malformed file into.
    @return Path to the copied results root.
    """
    copiedRoot = tmp_path / "GoogleTestResults"
    shutil.copytree(_realResultsRoot, copiedRoot)
    shutil.copy(_malformedFixture, copiedRoot / buildId / "gtest_malformed_injected.xml")
    return copiedRoot


def test_dashboardRoute_malformedXmlInLatestBuild_stillRendersAndShowsWarning(tmp_path):
    """!
    @brief FR-035 acceptance: one malformed XML does not crash the dashboard,
           and its parse error is surfaced as a warning with path + reason.
    """
    copiedRoot = _copyResultsTreeWithMalformedFileIn(tmp_path, "10")
    app = createApp(str(copiedRoot))
    client = app.test_client()

    with _capturedTemplateContext(app) as captured:
        response = client.get("/")

    assert response.status_code == 200
    warnings = captured[0]["warnings"]
    assert any(
        warning.kind == "parse_error" and warning.xmlPath.endswith("gtest_malformed_injected.xml")
        for warning in warnings
    )
    assert len(captured[0]["excludedFiles"]) == 1
    assert "gtest_malformed_injected.xml" in response.get_data(as_text=True)
    # The other 9 real XML files for build 10 still contribute their records.
    assert captured[0]["latestSummary"]["total"] == 1200


def test_buildDetailRoute_malformedXmlInThisBuild_listsOtherModulesAndWarns(tmp_path):
    """!
    @brief FR-035 acceptance: build-detail for the affected build still lists
           the other modules' tests and shows exactly its own warning.
    """
    copiedRoot = _copyResultsTreeWithMalformedFileIn(tmp_path, "10")
    app = createApp(str(copiedRoot))
    client = app.test_client()

    with _capturedTemplateContext(app) as captured:
        response = client.get("/builds/10")

    assert response.status_code == 200
    assert len(captured[0]["warnings"]) == 1
    assert captured[0]["warnings"][0].xmlPath.endswith("gtest_malformed_injected.xml")
    assert captured[0]["testRows"]
    assert captured[0]["buildSummary"]["total"] == 1200


def test_buildDetailRoute_malformedXmlInOtherBuild_showsNoWarningsHere(tmp_path):
    """!
    @brief FR-035: a build unaffected by the malformed file shows no warnings
           of its own, even though the snapshot as a whole has one.
    """
    copiedRoot = _copyResultsTreeWithMalformedFileIn(tmp_path, "10")
    app = createApp(str(copiedRoot))
    client = app.test_client()

    with _capturedTemplateContext(app) as captured:
        client.get("/builds/05")

    assert captured[0]["warnings"] == []
