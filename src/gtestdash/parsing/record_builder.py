"""!
@file record_builder.py
@brief Assemble one <testcase> into a complete ResultRecord (FR-004).
"""
from gtestdash.parsing.field_resolver import resolveFunction, resolveModule
from gtestdash.parsing.models import ResultRecord
from gtestdash.parsing.status_resolver import resolveStatus


def _extractFailureFields(testcaseElement):
    """!
    @brief Pull failure type/summary/detail out of a <testcase>'s <failure>, if any.
    @param testcaseElement xml.etree.ElementTree.Element for a <testcase>.
    @return Tuple (failure_type, failure_summary, failure_detail), each None
            when the testcase has no <failure> child.
    """
    failureElement = testcaseElement.find("failure")
    if failureElement is None:
        return None, None, None
    return failureElement.get("type"), failureElement.get("message"), failureElement.text


def buildNormalizedRecord(testsuiteElement, testcaseElement, properties, xmlPath, fallbackBuildId, fallbackTimestamp):
    """!
    @brief Build a complete ResultRecord for one <testcase> (FR-004, §4.3).
    @param testsuiteElement xml.etree.ElementTree.Element for the parent <testsuite>.
    @param testcaseElement xml.etree.ElementTree.Element for the <testcase>.
    @param properties Dict from field_resolver.extractProperties() for this suite.
    @param xmlPath Path to the source XML file (module-name fallback, §4.3).
    @param fallbackBuildId Folder-derived build id, used when jenkins_build_number
           is absent from properties.
    @param fallbackTimestamp <testsuites@timestamp>, used when the <testsuite>
           itself has no timestamp attribute.
    @return A fully populated ResultRecord.
    """
    failureType, failureSummary, failureDetail = _extractFailureFields(testcaseElement)
    lineAttr = testcaseElement.get("line")

    return ResultRecord(
        build_id=properties.get("jenkins_build_number") or fallbackBuildId,
        build_timestamp=testsuiteElement.get("timestamp") or fallbackTimestamp,
        module=resolveModule(properties, testcaseElement, xmlPath),
        suite=testsuiteElement.get("name"),
        function=resolveFunction(properties, testcaseElement),
        test_name=testcaseElement.get("name"),
        classname=testcaseElement.get("classname"),
        status=resolveStatus(testcaseElement),
        duration_seconds=float(testcaseElement.get("time") or 0.0),
        timestamp=testcaseElement.get("timestamp"),
        test_file=testcaseElement.get("file"),
        line=int(lineAttr) if lineAttr is not None else None,
        failure_type=failureType,
        failure_summary=failureSummary,
        failure_detail=failureDetail,
        source_file=properties.get("source_file"),
        synthetic_data=properties.get("synthetic_data"),
    )
