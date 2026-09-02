"""!
@file test_xml_parser.py
@brief Unit tests for FR-004/FR-035 GoogleTest XML parsing
       (src/gtestdash/parsing/xml_parser.py).
"""
import os

from gtestdash.parsing.xml_parser import parseTestsuiteFile

_fixtureDir = os.path.join(os.path.dirname(__file__), "..", "fixtures", "edge_cases")


def test_parseTestsuiteFile_parsesRealBuildXmlIntoRecords():
    """!
    @brief A real dataset XML parses into one ResultRecord per <testcase> (FR-004).
    """
    realXmlPath = os.path.join(
        os.path.dirname(__file__), "..", "..", "GoogleTestResults", "10", "gtest_child_lock_controller.xml"
    )

    records, warning = parseTestsuiteFile(realXmlPath)

    assert warning is None
    assert len(records) == 120
    failedCount = sum(1 for record in records if record.status == "FAILED")
    assert failedCount == 3


def test_parseTestsuiteFile_includesNonFailingTestsAsNormalRecords():
    """!
    @brief A <testcase> without <failure> still becomes a normal PASSED record (FR-004).
    """
    realXmlPath = os.path.join(
        os.path.dirname(__file__), "..", "..", "GoogleTestResults", "10", "gtest_child_lock_controller.xml"
    )

    records, _warning = parseTestsuiteFile(realXmlPath)

    passingRecord = next(r for r in records if r.test_name == "EvaluateLockRequest_NominalInput")
    assert passingRecord.status == "PASSED"
    assert passingRecord.failure_detail is None


def test_parseTestsuiteFile_returnsCountMismatchWarning_butStillIncludesRecords():
    """!
    @brief declared_mismatch.xml declares tests=5/failures=2 but only has 4
           <testcase> elements with 1 <failure>: the parsed records are still
           returned (parsable tests keep showing), with a count_mismatch
           warning attached (FR-008).
    """
    mismatchPath = os.path.join(_fixtureDir, "declared_mismatch.xml")

    records, warning = parseTestsuiteFile(mismatchPath)

    assert len(records) == 4
    assert warning is not None
    assert warning.kind == "count_mismatch"
    assert warning.xmlPath == mismatchPath


def test_parseTestsuiteFile_returnsWarningInsteadOfRaising_onMalformedXml():
    """!
    @brief A malformed XML file yields (empty records, a warning) rather than
           raising, so one bad file cannot crash the app (FR-035).
    """
    malformedPath = os.path.join(_fixtureDir, "malformed.xml")

    records, warning = parseTestsuiteFile(malformedPath)

    assert records == []
    assert warning is not None
    assert warning.xmlPath == malformedPath
    assert warning.kind == "parse_error"
