"""!
@file test_refresh_route.py
@brief Integration tests for POST /refresh against a temp copy of the dataset (FR-034).
"""
import os
import shutil

from _template_capture import capturedTemplateContext as _capturedTemplateContext

from gtestdash.web.app import createApp

## Real, read-only dataset root; copied per-test into tmp_path, never modified directly (CLAUDE.md).
_realResultsRoot = os.path.join(os.path.dirname(__file__), "..", "..", "GoogleTestResults")

## Minimal GoogleTest XML for a new build folder added after app startup.
_newBuildXml = """<?xml version="1.0" encoding="UTF-8"?>
<testsuites tests="1" failures="0" disabled="0" errors="0" time="0.001" timestamp="2026-09-02T00:00:00Z" name="AllTests">
  <testsuite name="NewBuild.Cases" tests="1" failures="0" disabled="0" skipped="0" errors="0" time="0.001" timestamp="2026-09-02T00:00:00Z">
    <properties>
      <property name="jenkins_build_number" value="11" />
      <property name="module" value="NewBuildModule" />
    </properties>
    <testcase name="NewBuild_Pass" classname="NewBuild.Cases" status="run" time="0.001" />
  </testsuite>
</testsuites>
"""


def _copyResultsTree(tmp_path):
    """!
    @brief Copy the real, read-only GoogleTestResults tree into tmp_path so a
           test can safely add build folders without touching the original.
    @param tmp_path pytest tmp_path fixture root.
    @return Path to the copied results root.
    """
    copiedRoot = tmp_path / "GoogleTestResults"
    shutil.copytree(_realResultsRoot, copiedRoot)
    return copiedRoot


def _addBuildElevenFolder(copiedRoot):
    """!
    @brief Add a new numeric build folder ("11") with one GoogleTest XML file.
    @param copiedRoot Path to the copied results root (a pathlib.Path).
    """
    newBuildDir = copiedRoot / "11"
    newBuildDir.mkdir()
    (newBuildDir / "gtest_new_build.xml").write_text(_newBuildXml)


def test_refreshRoute_afterAddingBuildFolder_recognizesItWithoutRestart(tmp_path):
    """!
    @brief FR-034 acceptance: a build folder added after startup is recognized
           by the same running app once /refresh is called, no restart required.
    """
    copiedRoot = _copyResultsTree(tmp_path)
    app = createApp(str(copiedRoot))
    client = app.test_client()
    beforeBuildIds = {record.build_id for record in app.config["SNAPSHOT"].records}
    assert "11" not in beforeBuildIds

    _addBuildElevenFolder(copiedRoot)
    response = client.post("/refresh")

    afterBuildIds = {record.build_id for record in app.config["SNAPSHOT"].records}
    assert response.status_code in (302, 303)
    assert "11" in afterBuildIds


def test_refreshRoute_afterAddingBuildFolder_becomesLatestBuildOnDashboard(tmp_path):
    """!
    @brief FR-034 acceptance: the newly added, higher-numbered build becomes the
           latest build shown on the dashboard once refreshed.
    """
    copiedRoot = _copyResultsTree(tmp_path)
    app = createApp(str(copiedRoot))
    client = app.test_client()
    _addBuildElevenFolder(copiedRoot)

    client.post("/refresh")

    with _capturedTemplateContext(app) as captured:
        client.get("/")

    assert captured[0]["latestSummary"]["buildId"] == "11"


def test_refreshRoute_redirectsBackToDashboardWhenNoReferrer(tmp_path):
    """!
    @brief FR-034: POST /refresh redirects somewhere sensible (the dashboard)
           when called with no Referer header.
    """
    copiedRoot = _copyResultsTree(tmp_path)
    app = createApp(str(copiedRoot))
    client = app.test_client()

    response = client.post("/refresh")

    assert response.status_code in (302, 303)
    assert response.headers["Location"].endswith("/")
