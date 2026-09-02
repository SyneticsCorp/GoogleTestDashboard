"""!
@file status_resolver.py
@brief Test status classification with priority ordering (FR-006).
"""

## Status precedence, highest first, per FR-006's mandated ordering.
_statusPriority = ["ERROR", "FAILED", "SKIPPED", "DISABLED", "PASSED"]


def _statusMarkersPresent(testcaseElement):
    """!
    @brief Determine which status markers are present on one <testcase>.
    @param testcaseElement xml.etree.ElementTree.Element for a <testcase>.
    @return Set of marker names among {"ERROR", "FAILED", "SKIPPED", "DISABLED"}.
    """
    markers = set()
    if testcaseElement.find("error") is not None:
        markers.add("ERROR")
    if testcaseElement.find("failure") is not None:
        markers.add("FAILED")
    if testcaseElement.find("skipped") is not None:
        markers.add("SKIPPED")
    if testcaseElement.get("status") == "notrun":
        markers.add("DISABLED")
    return markers


def resolveStatus(testcaseElement):
    """!
    @brief Classify one <testcase> into a normalized status (FR-006).
    @param testcaseElement xml.etree.ElementTree.Element for a <testcase>.
    @return One of "ERROR", "FAILED", "SKIPPED", "DISABLED", "PASSED", chosen by
            the highest-priority marker present; "PASSED" when none are.
    """
    markers = _statusMarkersPresent(testcaseElement)
    for candidateStatus in _statusPriority:
        if candidateStatus in markers:
            return candidateStatus
    return "PASSED"
