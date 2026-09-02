"""!
@file build_diff.py
@brief Failure-count/rate diff between the current build and the one before it (FR-011).
"""

## computeBuildDiff() result when there is no previous build to compare against.
_noPreviousDiff = {
    "failedDiff": None,
    "failureRateDiff": None,
    "direction": "no_previous",
    "previousFailed": None,
    "previousFailureRate": None,
}


def _diffDirection(failureRateDiff, failedDiff):
    """!
    @brief Classify a diff as increase/decrease/same, preferring the rate diff.
    @param failureRateDiff Failure-rate delta (current - previous), or None
           when either side's rate is "N/A".
    @param failedDiff Failed-count delta (current - previous).
    @return "increase", "decrease" or "same".
    """
    primaryDiff = failureRateDiff if failureRateDiff is not None else failedDiff
    if primaryDiff > 0:
        return "increase"
    if primaryDiff < 0:
        return "decrease"
    return "same"


def computeBuildDiff(currentSummary, previousSummary):
    """!
    @brief Diff the current build's failure count/rate against the previous build (FR-011).
    @param currentSummary Dict with at least "failed" (int) and "failureRate"
           (float or "N/A") - e.g. one entry from build_history.summarizeBuildsByBuild().
    @param previousSummary Same shape as currentSummary, for the immediately
           prior build, or None when currentSummary is the first build.
    @return Dict with failedDiff, failureRateDiff (both current - previous, or
            None when unavailable), direction ("increase"/"decrease"/"same"/
            "no_previous"), and the previous build's raw failed/failureRate.
    """
    if previousSummary is None:
        return dict(_noPreviousDiff)

    failedDiff = currentSummary["failed"] - previousSummary["failed"]
    currentRate, previousRate = currentSummary["failureRate"], previousSummary["failureRate"]
    ratesAreNumeric = isinstance(currentRate, (int, float)) and isinstance(previousRate, (int, float))
    failureRateDiff = round(currentRate - previousRate, 1) if ratesAreNumeric else None

    return {
        "failedDiff": failedDiff,
        "failureRateDiff": failureRateDiff,
        "direction": _diffDirection(failureRateDiff, failedDiff),
        "previousFailed": previousSummary["failed"],
        "previousFailureRate": previousRate,
    }
