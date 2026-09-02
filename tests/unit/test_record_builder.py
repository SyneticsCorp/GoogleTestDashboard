"""!
@file test_record_builder.py
@brief Unit tests for FR-004 normalized record assembly
       (src/gtestdash/parsing/record_builder.py).
"""
import xml.etree.ElementTree as elementTree

from gtestdash.parsing.record_builder import buildNormalizedRecord

_suiteWithFailureXml = """
<testsuite name="Widget.BehaviorTest" tests="1" failures="1" time="0.5" timestamp="2026-08-01T00:00:00Z">
  <properties>
    <property name="jenkins_build_number" value="7" />
    <property name="module" value="Widget" />
    <property name="tested_function" value="Rotate" />
    <property name="source_file" value="src/widget.cpp" />
    <property name="synthetic_data" value="true" />
  </properties>
  <testcase name="Rotate_NominalInput" classname="Widget.BehaviorTest" status="run"
            time="0.123" timestamp="2026-08-01T00:00:01Z"
            file="tests/widget_test.cpp" line="42">
    <failure message="rotation mismatch" type="AssertionFailure">expected 90 got 45</failure>
  </testcase>
</testsuite>
"""

_suiteWithoutBuildNumberXml = """
<testsuite name="Widget.PassingTest" tests="1" failures="0" time="0.1">
  <properties>
    <property name="module" value="Widget" />
  </properties>
  <testcase name="Rotate_PassCase" classname="Widget.PassingTest" status="run" time="0.05" />
</testsuite>
"""


def test_buildNormalizedRecord_populatesAllFieldsForFailingTest():
    """!
    @brief Every §4.3 field is populated from properties/testcase/failure (FR-004).
    """
    testsuite = elementTree.fromstring(_suiteWithFailureXml)
    testcase = testsuite.find("testcase")
    properties = {p.get("name"): p.get("value") for p in testsuite.find("properties")}

    record = buildNormalizedRecord(
        testsuiteElement=testsuite,
        testcaseElement=testcase,
        properties=properties,
        xmlPath="/results/07/gtest_widget.xml",
        fallbackBuildId="07",
        fallbackTimestamp="2026-08-01T00:00:00Z",
    )

    assert record.build_id == "7"
    assert record.build_timestamp == "2026-08-01T00:00:00Z"
    assert record.module == "Widget"
    assert record.suite == "Widget.BehaviorTest"
    assert record.function == "Rotate"
    assert record.test_name == "Rotate_NominalInput"
    assert record.classname == "Widget.BehaviorTest"
    assert record.status == "FAILED"
    assert record.duration_seconds == 0.123
    assert record.timestamp == "2026-08-01T00:00:01Z"
    assert record.test_file == "tests/widget_test.cpp"
    assert record.line == 42
    assert record.failure_type == "AssertionFailure"
    assert record.failure_summary == "rotation mismatch"
    assert record.failure_detail == "expected 90 got 45"
    assert record.source_file == "src/widget.cpp"
    assert record.synthetic_data == "true"


def test_buildNormalizedRecord_passingTestHasNoFailureFields():
    """!
    @brief A <testcase> without <failure> yields a normal PASSED record with
           no failure fields populated (FR-004).
    """
    testsuite = elementTree.fromstring(_suiteWithFailureXml)
    testcase = elementTree.fromstring(
        '<testcase name="Rotate_NoFailure" classname="Widget.BehaviorTest" status="run" time="0.05" />'
    )
    properties = {p.get("name"): p.get("value") for p in testsuite.find("properties")}

    record = buildNormalizedRecord(
        testsuiteElement=testsuite,
        testcaseElement=testcase,
        properties=properties,
        xmlPath="/results/07/gtest_widget.xml",
        fallbackBuildId="07",
        fallbackTimestamp="2026-08-01T00:00:00Z",
    )

    assert record.status == "PASSED"
    assert record.failure_type is None
    assert record.failure_summary is None
    assert record.failure_detail is None


def test_buildNormalizedRecord_fallsBackToFolderBuildIdAndSuitesTimestamp():
    """!
    @brief No jenkins_build_number/testsuite timestamp: fall back to the
           folder-derived build id and the <testsuites> timestamp (§4.3).
    """
    testsuite = elementTree.fromstring(_suiteWithoutBuildNumberXml)
    testcase = testsuite.find("testcase")
    properties = {p.get("name"): p.get("value") for p in testsuite.find("properties")}

    record = buildNormalizedRecord(
        testsuiteElement=testsuite,
        testcaseElement=testcase,
        properties=properties,
        xmlPath="/results/03/gtest_widget.xml",
        fallbackBuildId="03",
        fallbackTimestamp="2026-07-01T00:00:00Z",
    )

    assert record.build_id == "03"
    assert record.build_timestamp == "2026-07-01T00:00:00Z"
