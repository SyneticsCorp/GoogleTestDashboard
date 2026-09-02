"""!
@file test_module_trend.py
@brief Unit tests for per-module failure-rate trend across builds (src/gtestdash/aggregation/module_trend.py, FR-020).
"""
from gtestdash.aggregation.module_trend import computeModuleTrendAcrossBuilds
from gtestdash.parsing.models import ResultRecord


def _makeRecord(buildId, module, status):
    """!
    @brief Build a minimal ResultRecord for module-trend tests.
    @param buildId build_id to assign.
    @param module Module name to assign.
    @param status Normalized status string.
    @return A ResultRecord with placeholder values for every other field.
    """
    return ResultRecord(
        build_id=buildId,
        build_timestamp="2026-01-01T00:00:00Z",
        module=module,
        suite=f"{module}.Suite",
        function="Func",
        test_name="Func_Case",
        classname=f"{module}.Suite",
        status=status,
        duration_seconds=0.1,
        timestamp=None,
        test_file=None,
        line=None,
        failure_type=None,
        failure_summary=None,
        failure_detail=None,
        source_file=None,
        synthetic_data=None,
    )


def _twoModuleThreeBuildRecords():
    """!
    @brief Records for module "Alpha" across builds 01/02, plus unrelated module "Beta".
    @return Flat ResultRecord list for module-filtering and ordering tests.
    """
    return [
        _makeRecord("02", "Alpha", "PASSED"),
        _makeRecord("02", "Alpha", "FAILED"),
        _makeRecord("01", "Alpha", "PASSED"),
        _makeRecord("01", "Alpha", "PASSED"),
        _makeRecord("01", "Beta", "FAILED"),
    ]


def test_computeModuleTrendAcrossBuilds_filtersToGivenModuleOnly():
    """!
    @brief Records belonging to other modules are excluded from the trend (FR-020).
    """
    trend = computeModuleTrendAcrossBuilds(_twoModuleThreeBuildRecords(), "Alpha")

    assert sum(point["total"] for point in trend) == 4


def test_computeModuleTrendAcrossBuilds_ordersPointsByBuildIdNumericAscending():
    """!
    @brief Build "10" would sort after build "02", not lexically before it (FR-020).
    """
    trend = computeModuleTrendAcrossBuilds(_twoModuleThreeBuildRecords(), "Alpha")

    assert [point["buildId"] for point in trend] == ["01", "02"]


def test_computeModuleTrendAcrossBuilds_computesTotalFailedAndFailureRatePerBuild():
    """!
    @brief Each point carries total/failed/failureRate computed from that build's module records (FR-007, FR-020).
    """
    trend = computeModuleTrendAcrossBuilds(_twoModuleThreeBuildRecords(), "Alpha")

    assert trend[0] == {"buildId": "01", "total": 2, "failed": 0, "failureRate": 0.0}
    assert trend[1] == {"buildId": "02", "total": 2, "failed": 1, "failureRate": 50.0}
