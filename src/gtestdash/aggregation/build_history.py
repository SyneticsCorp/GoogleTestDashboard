"""!
@file build_history.py
@brief Per-build summary rows for the build history table and trend/diff inputs (FR-017).

Builds the shared "build summary" shape that latest_build.resolveLatestBuild(),
build_diff.computeBuildDiff() and trend.buildFailureRateTrend() all consume, so
those modules stay pure functions over plain dicts rather than each re-deriving
counts from records themselves.
"""
from gtestdash.aggregation.build_summary import computeCounts, computeFailureRate
from gtestdash.aggregation.grouping import groupRecordsByBuild, numericBuildIdSortKey


def _earliestTimestamp(buildRecords):
    """!
    @brief Pick a single representative timestamp for a build's records.
    @param buildRecords ResultRecord list belonging to one build.
    @return The earliest non-None build_timestamp among them, or None.
    """
    timestamps = [record.build_timestamp for record in buildRecords if record.build_timestamp]
    return min(timestamps) if timestamps else None


def _summarizeOneBuild(buildId, buildRecords):
    """!
    @brief Fold one build's records into a summary row (FR-007, FR-017).
    @param buildId Build id these records belong to.
    @param buildRecords ResultRecord list for that build.
    @return Dict with buildId, buildTimestamp, total/passed/failed/error/
            skipped/disabled counts, failureRate, durationSeconds and buildUrl.
    """
    counts = computeCounts(buildRecords)
    return {
        "buildId": buildId,
        "buildTimestamp": _earliestTimestamp(buildRecords),
        "total": counts["total"],
        "passed": counts["passed"],
        "failed": counts["failed"],
        "error": counts["error"],
        "skipped": counts["skipped"],
        "disabled": counts["disabled"],
        "failureRate": computeFailureRate(counts),
        "durationSeconds": round(sum(record.duration_seconds for record in buildRecords), 3),
        "buildUrl": f"/builds/{buildId}",
    }


def summarizeBuildsByBuild(records):
    """!
    @brief Group records by build and summarize each build (FR-017).
    @param records Full list of ResultRecord across every build.
    @return List of per-build summary dicts (see _summarizeOneBuild()), sorted
            by build id ascending, numeric ids first ("09" before "10").
    """
    grouped = groupRecordsByBuild(records)
    summaries = [_summarizeOneBuild(buildId, buildRecords) for buildId, buildRecords in grouped.items()]
    summaries.sort(key=lambda summary: numericBuildIdSortKey(summary["buildId"]))
    return summaries
