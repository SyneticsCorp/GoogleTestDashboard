"""!
@file test_build_history.py
@brief Unit tests for per-build summarization (src/gtestdash/aggregation/build_history.py, FR-017).
"""
from gtestdash.aggregation.build_history import summarizeBuildsByBuild
from gtestdash.parsing.models import ResultRecord


def _makeRecord(buildId, status, duration, timestamp):
    """!
    @brief Build a minimal ResultRecord for build-history summarization tests.
    @param buildId build_id to assign.
    @param status Normalized status string.
    @param duration duration_seconds value.
    @param timestamp build_timestamp value.
    @return A ResultRecord with placeholder values for every other field.
    """
    return ResultRecord(
        build_id=buildId,
        build_timestamp=timestamp,
        module="Mod",
        suite="Mod.Suite",
        function="Func",
        test_name="Func_Case",
        classname="Mod.Suite",
        status=status,
        duration_seconds=duration,
        timestamp=None,
        test_file=None,
        line=None,
        failure_type=None,
        failure_summary=None,
        failure_detail=None,
        source_file=None,
        synthetic_data=None,
    )


def test_summarizeBuildsByBuild_computesCountsRateAndDurationPerBuild():
    """!
    @brief One build's records fold into total/failed/failureRate/durationSeconds (FR-007, FR-017).
    """
    records = [
        _makeRecord("01", "PASSED", 0.5, "2026-01-01T00:00:00Z"),
        _makeRecord("01", "FAILED", 0.25, "2026-01-01T00:00:05Z"),
    ]

    summaries = summarizeBuildsByBuild(records)

    assert len(summaries) == 1
    summary = summaries[0]
    assert summary["buildId"] == "01"
    assert summary["total"] == 2
    assert summary["passed"] == 1
    assert summary["failed"] == 1
    assert summary["failureRate"] == 50.0
    assert summary["durationSeconds"] == 0.75
    assert summary["buildTimestamp"] == "2026-01-01T00:00:00Z"
    assert summary["buildUrl"] == "/builds/01"


def test_summarizeBuildsByBuild_ordersBuildsNumericallyAscending():
    """!
    @brief Build "10" sorts after build "09", not lexically before it (FR-002 rule extended).
    """
    records = [
        _makeRecord("10", "PASSED", 0.1, "2026-01-10T00:00:00Z"),
        _makeRecord("02", "PASSED", 0.1, "2026-01-02T00:00:00Z"),
        _makeRecord("09", "PASSED", 0.1, "2026-01-09T00:00:00Z"),
    ]

    summaries = summarizeBuildsByBuild(records)

    assert [summary["buildId"] for summary in summaries] == ["02", "09", "10"]
