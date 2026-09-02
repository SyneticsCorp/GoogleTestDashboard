"""!
@file validation.py
@brief Compare XML-declared counts against recomputed counts (FR-008).
"""
from gtestdash.parsing.models import ParseWarning


def compareDeclaredVsComputed(declaredCounts, computedCounts, xmlPath):
    """!
    @brief Diff declared vs. recomputed tests/failures/errors/disabled/skipped (FR-008).
    @param declaredCounts Dict of counts declared in the XML (root attributes).
    @param computedCounts Dict of counts recomputed from parsed records.
    @param xmlPath Path to the XML file these counts came from.
    @return None when every key matches; otherwise a ParseWarning naming the
            mismatched keys and carrying both count dicts (and xmlPath) for
            display, per FR-008's acceptance criterion.
    """
    mismatchedKeys = sorted(key for key in declaredCounts if declaredCounts[key] != computedCounts.get(key))
    if not mismatchedKeys:
        return None

    message = "declared vs computed count mismatch for: " + ", ".join(mismatchedKeys)
    return ParseWarning(
        xmlPath=xmlPath,
        kind="count_mismatch",
        message=message,
        declaredCounts=dict(declaredCounts),
        computedCounts=dict(computedCounts),
    )
