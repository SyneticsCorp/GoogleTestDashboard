"""!
@file test_trend.py
@brief Unit tests for the failure-rate trend series (src/gtestdash/aggregation/trend.py, FR-012/013).
"""
from gtestdash.aggregation.trend import buildFailureRateTrend


def _makeSummary(buildId, failureRate, total=1200, failed=0):
    """!
    @brief Build a minimal build-summary dict as trend input.
    @param buildId Build id string.
    @param failureRate Failure rate value (float or "N/A").
    @param total Total test count for this build.
    @param failed Failed test count for this build.
    @return Dict matching build_history.summarizeBuildsByBuild()'s shape.
    """
    return {
        "buildId": buildId,
        "buildTimestamp": f"2026-01-{buildId}T00:00:00Z",
        "total": total,
        "failed": failed,
        "failureRate": failureRate,
        "buildUrl": f"/builds/{buildId}",
    }


def test_buildFailureRateTrend_ordersPointsByBuildIdAscending():
    """!
    @brief Points are numeric-build-id ascending regardless of input order (FR-012).
    """
    summaries = [_makeSummary("10", 2.0), _makeSummary("02", 4.0), _makeSummary("09", 4.0)]

    trendPoints = buildFailureRateTrend(summaries)

    assert [point["buildId"] for point in trendPoints] == ["02", "09", "10"]


def test_buildFailureRateTrend_pointCarriesTotalFailedRateAndUrl():
    """!
    @brief Each point exposes what a trend tooltip and drilldown need (FR-013).
    """
    summaries = [_makeSummary("08", 10.0, total=1200, failed=120)]

    trendPoints = buildFailureRateTrend(summaries)

    point = trendPoints[0]
    assert point["total"] == 1200
    assert point["failed"] == 120
    assert point["failureRate"] == 10.0
    assert point["buildUrl"] == "/builds/08"
