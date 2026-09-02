"""!
@file trend.py
@brief Build-number-ordered failure-rate trend series (FR-012, FR-013).
"""
from gtestdash.aggregation.grouping import numericBuildIdSortKey

## Build-summary keys copied verbatim onto each trend point (FR-013).
_trendPointKeys = ["buildId", "buildTimestamp", "total", "failed", "failureRate", "buildUrl"]


def buildFailureRateTrend(buildSummaries):
    """!
    @brief Order build summaries into a chart-ready failure-rate trend (FR-012, FR-013).
    @param buildSummaries List of per-build summary dicts, as returned by
           build_history.summarizeBuildsByBuild() (any input order accepted).
    @return List of trend points sorted by build id ascending ("09" before
            "10"), each carrying buildId, buildTimestamp, total, failed,
            failureRate and buildUrl for tooltip display and drilldown (FR-013).
    """
    sortedSummaries = sorted(buildSummaries, key=lambda summary: numericBuildIdSortKey(summary["buildId"]))
    return [{key: summary[key] for key in _trendPointKeys} for summary in sortedSummaries]
