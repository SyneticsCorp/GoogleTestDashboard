"""!
@file test_status_resolver.py
@brief Unit tests for FR-006 status priority resolution
       (src/gtestdash/parsing/status_resolver.py).

Uses tests/fixtures/edge_cases/status_priority_conflict.xml, a synthetic
truth-table fixture covering every marker combination, since the real
GoogleTestResults dataset (read-only, per CLAUDE.md) has no error/skipped/
disabled samples.
"""
import os
import xml.etree.ElementTree as elementTree

import pytest

from gtestdash.parsing.status_resolver import resolveStatus

## Path to the shared status-priority truth-table fixture.
_fixturePath = os.path.join(
    os.path.dirname(__file__), "..", "fixtures", "edge_cases", "status_priority_conflict.xml"
)


def _loadTestcase(testCaseName):
    """!
    @brief Parse the fixture and return the <testcase> element with the given name.
    @param testCaseName Value of the testcase's "name" attribute to find.
    @return xml.etree.ElementTree.Element for that testcase.
    """
    tree = elementTree.parse(_fixturePath)
    for testcase in tree.getroot().iter("testcase"):
        if testcase.get("name") == testCaseName:
            return testcase
    raise AssertionError(f"fixture testcase not found: {testCaseName}")


@pytest.mark.parametrize(
    "testCaseName,expectedStatus",
    [
        ("PlainPass", "PASSED"),
        ("OnlyFailure", "FAILED"),
        ("OnlyError", "ERROR"),
        ("OnlySkipped", "SKIPPED"),
        ("OnlyDisabledStatusAttr", "DISABLED"),
        ("FailureAndError", "ERROR"),
        ("SkippedAndFailure", "FAILED"),
        ("DisabledAndSkipped", "SKIPPED"),
    ],
)
def test_resolveStatus_appliesPriorityTruthTable(testCaseName, expectedStatus):
    """!
    @brief FR-006: ERROR > FAILED > SKIPPED > DISABLED > PASSED, per case.
    """
    testcaseElement = _loadTestcase(testCaseName)

    assert resolveStatus(testcaseElement) == expectedStatus
