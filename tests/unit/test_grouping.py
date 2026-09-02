"""!
@file test_grouping.py
@brief Unit tests for record-by-build grouping (src/gtestdash/aggregation/grouping.py).
"""
from gtestdash.aggregation.grouping import groupRecordsByBuild, numericBuildIdSortKey
from gtestdash.parsing.models import ResultRecord


def _makeRecord(buildId):
    """!
    @brief Build a minimal ResultRecord carrying only the build_id under test.
    @param buildId build_id value to assign.
    @return A ResultRecord with placeholder values for every other field.
    """
    return ResultRecord(
        build_id=buildId,
        build_timestamp=None,
        module="Mod",
        suite="Mod.Suite",
        function="Func",
        test_name="Func_Case",
        classname="Mod.Suite",
        status="PASSED",
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


def test_groupRecordsByBuild_splitsRecordsIntoPerBuildLists():
    """!
    @brief Records land under the dict key matching their own build_id, in order.
    """
    records = [_makeRecord("01"), _makeRecord("02"), _makeRecord("01")]

    grouped = groupRecordsByBuild(records)

    assert set(grouped.keys()) == {"01", "02"}
    assert len(grouped["01"]) == 2
    assert len(grouped["02"]) == 1


def test_numericBuildIdSortKey_ordersDoubleDigitBuildsNumerically():
    """!
    @brief "10" sorts after "09" under this key, not lexically before it.
    """
    buildIds = ["10", "09", "02"]

    orderedIds = sorted(buildIds, key=numericBuildIdSortKey)

    assert orderedIds == ["02", "09", "10"]
