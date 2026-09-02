"""!
@file test_build_diff.py
@brief Unit tests for build-over-build diffing (src/gtestdash/aggregation/build_diff.py, FR-011).
"""
from gtestdash.aggregation.build_diff import computeBuildDiff


def test_computeBuildDiff_reportsDecrease_whenFailureRateDrops():
    """!
    @brief Build 10 vs build 09: 4.0% -> 2.0% is a 2.0pp decrease (FR-011 acceptance).
    """
    current = {"failed": 24, "failureRate": 2.0}
    previous = {"failed": 48, "failureRate": 4.0}

    diff = computeBuildDiff(current, previous)

    assert diff["failureRateDiff"] == -2.0
    assert diff["failedDiff"] == -24
    assert diff["direction"] == "decrease"
    assert diff["previousFailureRate"] == 4.0


def test_computeBuildDiff_reportsIncrease_whenFailureRateRises():
    """!
    @brief A higher current failure rate than the previous build is an increase.
    """
    current = {"failed": 10, "failureRate": 5.0}
    previous = {"failed": 6, "failureRate": 3.0}

    diff = computeBuildDiff(current, previous)

    assert diff["direction"] == "increase"
    assert diff["failureRateDiff"] == 2.0


def test_computeBuildDiff_reportsSame_whenFailureRateUnchanged():
    """!
    @brief An identical failure rate across builds is neither increase nor decrease.
    """
    current = {"failed": 5, "failureRate": 1.0}
    previous = {"failed": 5, "failureRate": 1.0}

    diff = computeBuildDiff(current, previous)

    assert diff["direction"] == "same"
    assert diff["failureRateDiff"] == 0.0


def test_computeBuildDiff_reportsNoPrevious_whenThereIsNoPriorBuild():
    """!
    @brief The very first build has no predecessor to diff against.
    """
    current = {"failed": 3, "failureRate": 1.5}

    diff = computeBuildDiff(current, None)

    assert diff["direction"] == "no_previous"
    assert diff["failedDiff"] is None
    assert diff["failureRateDiff"] is None
