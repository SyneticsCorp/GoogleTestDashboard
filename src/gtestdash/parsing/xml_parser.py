"""!
@file xml_parser.py
@brief Parse one GoogleTest XML file into normalized records (FR-004, FR-035).
"""
import os
import xml.etree.ElementTree as elementTree

from gtestdash.parsing.field_resolver import extractProperties
from gtestdash.parsing.models import ParseWarning
from gtestdash.parsing.record_builder import buildNormalizedRecord
from gtestdash.parsing.validation import compareDeclaredVsComputed

## Declared/computed count keys shared by _extractDeclaredCounts() and
## _tallyComputedCounts() so compareDeclaredVsComputed() can diff them (FR-008).
_declaredCountKeys = ["tests", "failures", "errors", "disabled", "skipped"]

## Normalized status -> declared-style count key it contributes to (FR-008).
_statusToCountKey = {"FAILED": "failures", "ERROR": "errors", "DISABLED": "disabled", "SKIPPED": "skipped"}


def _buildRecordsForSuite(testsuiteElement, xmlPath, fallbackBuildId, fallbackTimestamp):
    """!
    @brief Build a ResultRecord for every <testcase> in one <testsuite>.
    @param testsuiteElement xml.etree.ElementTree.Element for the <testsuite>.
    @param xmlPath Path to the source XML file.
    @param fallbackBuildId Folder-derived build id fallback.
    @param fallbackTimestamp <testsuites@timestamp> fallback.
    @return List of ResultRecord, one per <testcase> in this suite.
    """
    properties = extractProperties(testsuiteElement)
    return [
        buildNormalizedRecord(testsuiteElement, testcase, properties, xmlPath, fallbackBuildId, fallbackTimestamp)
        for testcase in testsuiteElement.findall("testcase")
    ]


def _extractDeclaredCounts(rootElement):
    """!
    @brief Sum tests/failures/errors/disabled/skipped across all <testsuite> children (FR-008).
    @param rootElement xml.etree.ElementTree.Element for the <testsuites> root.
    @return Dict of declared counts; suites missing an attribute contribute 0.
    """
    declaredCounts = {key: 0 for key in _declaredCountKeys}
    for testsuiteElement in rootElement.findall("testsuite"):
        for key in _declaredCountKeys:
            declaredCounts[key] += int(testsuiteElement.get(key) or 0)
    return declaredCounts


def _tallyComputedCounts(records):
    """!
    @brief Recompute declared-style counts directly from parsed records (FR-008).
    @param records List of ResultRecord already built for this file.
    @return Dict with the same keys as _extractDeclaredCounts(), computed from
            each record's normalized status rather than trusted from the XML.
    """
    computedCounts = {"tests": len(records)}
    computedCounts.update({key: 0 for key in _declaredCountKeys if key != "tests"})
    for record in records:
        countKey = _statusToCountKey.get(record.status)
        if countKey:
            computedCounts[countKey] += 1
    return computedCounts


def parseTestsuiteFile(xmlPath):
    """!
    @brief Parse one GoogleTest XML file into normalized ResultRecords (FR-004).

    A malformed file (XML parse failure) never raises: it is signalled as a
    ParseWarning with no records, so callers can exclude it and keep
    processing the rest of the dataset (FR-035). A well-formed file whose
    declared tests/failures/errors/disabled/skipped counts disagree with the
    recomputed counts still returns its records, alongside a count-mismatch
    ParseWarning (FR-008).

    @param xmlPath Path to a GoogleTest results XML file.
    @return Tuple (records, warning): records is a list of ResultRecord (empty
            only on parse failure); warning is None when parsing succeeded and
            counts matched, else a ParseWarning.
    """
    try:
        tree = elementTree.parse(xmlPath)
    except elementTree.ParseError as parseError:
        return [], ParseWarning(xmlPath=xmlPath, kind="parse_error", message=str(parseError))

    rootElement = tree.getroot()
    fallbackBuildId = os.path.basename(os.path.dirname(xmlPath))
    fallbackTimestamp = rootElement.get("timestamp")

    records = []
    for testsuiteElement in rootElement.findall("testsuite"):
        records.extend(_buildRecordsForSuite(testsuiteElement, xmlPath, fallbackBuildId, fallbackTimestamp))

    declaredCounts = _extractDeclaredCounts(rootElement)
    computedCounts = _tallyComputedCounts(records)
    warning = compareDeclaredVsComputed(declaredCounts, computedCounts, xmlPath)
    return records, warning
