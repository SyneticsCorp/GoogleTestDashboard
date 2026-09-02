"""!
@file test_validation.py
@brief Unit tests for FR-008 declared-vs-computed count validation
       (src/gtestdash/parsing/validation.py).
"""
import os
import xml.etree.ElementTree as elementTree

from gtestdash.parsing.validation import compareDeclaredVsComputed

_fixturePath = os.path.join(
    os.path.dirname(__file__), "..", "fixtures", "edge_cases", "declared_mismatch.xml"
)


def test_compareDeclaredVsComputed_returnsNone_whenCountsMatch():
    """!
    @brief No warning is raised when declared and computed counts agree (FR-008).
    """
    matchingCounts = {"tests": 4, "failures": 1, "errors": 0, "disabled": 0, "skipped": 0}

    warning = compareDeclaredVsComputed(matchingCounts, dict(matchingCounts), "some.xml")

    assert warning is None


def test_compareDeclaredVsComputed_flagsMismatch_withXmlPathDeclaredAndComputed():
    """!
    @brief declared_mismatch.xml declares tests=5/failures=2 at the root but
           actually contains 4 testcases with 1 failure; the warning must
           carry the XML path, the declared counts, and the computed counts
           (FR-008's acceptance criterion).
    """
    root = elementTree.parse(_fixturePath).getroot()
    declaredCounts = {
        "tests": int(root.get("tests")),
        "failures": int(root.get("failures")),
        "errors": int(root.get("errors")),
        "disabled": int(root.get("disabled")),
        "skipped": 0,
    }
    computedCounts = {"tests": 4, "failures": 1, "errors": 0, "disabled": 0, "skipped": 0}

    warning = compareDeclaredVsComputed(declaredCounts, computedCounts, _fixturePath)

    assert warning is not None
    assert warning.xmlPath == _fixturePath
    assert warning.declaredCounts == {"tests": 5, "failures": 2, "errors": 0, "disabled": 0, "skipped": 0}
    assert warning.computedCounts == computedCounts
    assert "tests" in warning.message
    assert "failures" in warning.message
