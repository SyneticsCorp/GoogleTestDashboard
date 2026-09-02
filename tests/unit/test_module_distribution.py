"""!
@file test_module_distribution.py
@brief Unit tests for module failure distribution (src/gtestdash/aggregation/module_distribution.py, FR-014/015).
"""
from gtestdash.aggregation.module_distribution import buildModuleDrilldownUrl, computeModuleDistribution
from gtestdash.parsing.models import ResultRecord


def _makeRecord(buildId, module, status):
    """!
    @brief Build a minimal ResultRecord for module-distribution tests.
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


def _twoModuleTwoBuildRecords():
    """!
    @brief Two builds ("01", "02") each with two modules, one failure per build.
    @return Flat ResultRecord list for scope-filtering tests.
    """
    return [
        _makeRecord("01", "Alpha", "FAILED"),
        _makeRecord("01", "Alpha", "PASSED"),
        _makeRecord("01", "Beta", "PASSED"),
        _makeRecord("02", "Alpha", "PASSED"),
        _makeRecord("02", "Beta", "FAILED"),
        _makeRecord("02", "Beta", "PASSED"),
    ]


def test_computeModuleDistribution_latestScope_onlyCountsHighestBuild():
    """!
    @brief Default "latest" scope only tallies the highest-numbered build (FR-014).
    """
    distribution = computeModuleDistribution(_twoModuleTwoBuildRecords(), "latest")

    assert {entry["module"]: entry["failed"] for entry in distribution} == {"Alpha": 0, "Beta": 1}


def test_computeModuleDistribution_cumulativeScope_sumsAcrossAllBuilds():
    """!
    @brief "cumulative" scope tallies failures across every build (FR-014).
    """
    distribution = computeModuleDistribution(_twoModuleTwoBuildRecords(), "cumulative")

    assert {entry["module"]: entry["failed"] for entry in distribution} == {"Alpha": 1, "Beta": 1}


def test_computeModuleDistribution_specificBuildScope_filtersToThatBuildOnly():
    """!
    @brief A specific build id scope tallies only that build's records (FR-014).
    """
    distribution = computeModuleDistribution(_twoModuleTwoBuildRecords(), "01")

    assert {entry["module"]: entry["failed"] for entry in distribution} == {"Alpha": 1, "Beta": 0}


def test_computeModuleDistribution_sortsByFailedCountDescending():
    """!
    @brief Modules with more failures sort first (FR-014).
    """
    distribution = computeModuleDistribution(_twoModuleTwoBuildRecords(), "cumulative")

    assert distribution[0]["failed"] >= distribution[1]["failed"]


def test_buildModuleDrilldownUrl_pointsToModuleDetailWithFailedOnlyFilter():
    """!
    @brief The drilldown URL follows Requirements.md §5's module-detail path and
           pre-enables the failed-only filter (FR-015).
    """
    url = buildModuleDrilldownUrl("10", "ChildLockController")

    assert url == "/builds/10/modules/ChildLockController?failedOnly=true"
