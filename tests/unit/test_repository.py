"""!
@file test_repository.py
@brief Unit tests for buildSnapshot() orchestration (src/gtestdash/repository.py).

Uses a small synthetic results tree (not the read-only GoogleTestResults
dataset) so both the happy path and the malformed-file isolation path (FR-035)
can be exercised cheaply and deterministically.
"""
from gtestdash.repository import buildSnapshot

_goodSuiteXml = """<?xml version="1.0" encoding="UTF-8"?>
<testsuites tests="2" failures="1" disabled="0" errors="0" time="0.01" timestamp="2026-01-01T00:00:00Z" name="AllTests">
  <testsuite name="Widget.Cases" tests="2" failures="1" disabled="0" skipped="0" errors="0" time="0.01" timestamp="2026-01-01T00:00:00Z">
    <properties>
      <property name="jenkins_build_number" value="1" />
      <property name="module" value="Widget" />
    </properties>
    <testcase name="Widget_Pass" classname="Widget.Cases" status="run" time="0.005" />
    <testcase name="Widget_Fail" classname="Widget.Cases" status="run" time="0.005">
      <failure message="boom" type="AssertionFailure">details</failure>
    </testcase>
  </testsuite>
</testsuites>
"""

_brokenSuiteXml = "<testsuites><testsuite><testcase name=\"Unterminated\">"


def _makeResultsTree(tmp_path):
    """!
    @brief Build a two-build synthetic results tree: one good file, one broken.
    @param tmp_path pytest tmp_path fixture root.
    @return Path to the results root directory.
    """
    build1 = tmp_path / "01"
    build1.mkdir()
    (build1 / "gtest_widget.xml").write_text(_goodSuiteXml)

    build2 = tmp_path / "02"
    build2.mkdir()
    (build2 / "gtest_broken.xml").write_text(_brokenSuiteXml)

    return tmp_path


def test_buildSnapshot_collectsRecordsAcrossAllBuildFolders(tmp_path):
    """!
    @brief Records from every build folder's XML files are combined (FR-002/003/004).
    """
    resultsRoot = _makeResultsTree(tmp_path)

    snapshot = buildSnapshot(str(resultsRoot))

    assert len(snapshot.records) == 2
    assert {record.test_name for record in snapshot.records} == {"Widget_Pass", "Widget_Fail"}


def test_buildSnapshot_isolatesMalformedFile_withoutLosingGoodRecords(tmp_path):
    """!
    @brief A malformed XML is excluded and warned about, but the good file's
           records still appear in the snapshot (FR-035).
    """
    resultsRoot = _makeResultsTree(tmp_path)

    snapshot = buildSnapshot(str(resultsRoot))

    assert len(snapshot.excludedFiles) == 1
    assert snapshot.excludedFiles[0].endswith("gtest_broken.xml")
    assert any(warning.kind == "parse_error" for warning in snapshot.warnings)
    assert len(snapshot.records) == 2
