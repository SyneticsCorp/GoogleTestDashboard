"""!
@file module_trend.py
@brief Per-module failure-rate trend across builds, for the module detail page (FR-020).
"""
from gtestdash.aggregation.build_summary import computeCounts, computeFailureRate
from gtestdash.aggregation.grouping import groupRecordsByBuild, numericBuildIdSortKey


def _summarizeModuleBuildPoint(buildId, buildModuleRecords):
    """!
    @brief Fold one build's already-module-filtered records into one trend point (FR-020).
    @param buildId Build id these records belong to.
    @param buildModuleRecords ResultRecord list for one module within one build.
    @return Dict with buildId, total, failed and failureRate.
    """
    counts = computeCounts(buildModuleRecords)
    return {
        "buildId": buildId,
        "total": counts["total"],
        "failed": counts["failed"],
        "failureRate": computeFailureRate(counts),
    }


def computeModuleTrendAcrossBuilds(records, module):
    """!
    @brief Compute one module's failure-rate trend across every build it appears in (FR-020).
    @param records Full list of ResultRecord across every build.
    @param module Module name to filter to.
    @return List of per-build trend points (see _summarizeModuleBuildPoint()),
            sorted by build id ascending, numeric ids first ("09" before "10").
    """
    moduleRecords = [record for record in records if record.module == module]
    grouped = groupRecordsByBuild(moduleRecords)
    points = [_summarizeModuleBuildPoint(buildId, buildRecords) for buildId, buildRecords in grouped.items()]
    points.sort(key=lambda point: numericBuildIdSortKey(point["buildId"]))
    return points
