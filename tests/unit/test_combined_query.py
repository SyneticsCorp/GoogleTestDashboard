"""!
@file test_combined_query.py
@brief Unit tests for the FR-029 single-entry-point query (src/gtestdash/query/combined_query.py).
"""
from gtestdash.parsing.models import ResultRecord
from gtestdash.query.combined_query import runCombinedQuery


def _makeRecord(buildId, module, status, function, suite, testName):
    """!
    @brief Build a minimal ResultRecord for combined-query tests.
    @param buildId build_id to assign.
    @param module Module name to assign.
    @param status Normalized status string.
    @param function tested_function value to assign.
    @param suite testsuite name to assign.
    @param testName test_name to assign.
    @return A ResultRecord with placeholder values for every other field.
    """
    return ResultRecord(
        build_id=buildId,
        build_timestamp="2026-01-01T00:00:00Z",
        module=module,
        suite=suite,
        function=function,
        test_name=testName,
        classname=f"{module}.{suite}",
        status=status,
        duration_seconds=0.4,
        timestamp=None,
        test_file="widget_test.cc",
        line=9,
        failure_type=None,
        failure_summary=None,
        failure_detail=None,
        source_file=None,
        synthetic_data=None,
    )


def _fixtureRecords():
    """!
    @brief Build 10's ChildLockController (3 of 4 records FAILED) plus another build/module.
    @return Flat ResultRecord list mirroring the FR-029 acceptance shape at small scale.
    """
    return [
        _makeRecord("10", "ChildLockController", "FAILED", "Lock", "Alpha.LockSuite", "Case_A"),
        _makeRecord("10", "ChildLockController", "FAILED", "Lock", "Alpha.LockSuite", "Case_B"),
        _makeRecord("10", "ChildLockController", "FAILED", "Unlock", "Alpha.UnlockSuite", "Case_C"),
        _makeRecord("10", "ChildLockController", "PASSED", "Unlock", "Alpha.UnlockSuite", "Case_D"),
        _makeRecord("10", "Beta", "PASSED", "Sense", "Beta.SenseSuite", "Case_E"),
        _makeRecord("09", "ChildLockController", "FAILED", "Lock", "Alpha.LockSuite", "Case_F"),
    ]


def test_runCombinedQuery_noArguments_returnsEveryRecord():
    """!
    @brief FR-029 "전체 초기화" acceptance: calling with no filters returns every record.
    """
    result = runCombinedQuery(_fixtureRecords())

    assert result["totalMatches"] == 6


def test_runCombinedQuery_buildAndModuleAndFailedOnly_narrowsToThreeRecords():
    """!
    @brief FR-029 acceptance shape: build + module + failed-only combine to a small result.
    """
    result = runCombinedQuery(_fixtureRecords(), buildId="10", module="ChildLockController", failedOnly=True)

    assert result["totalMatches"] == 3
    assert {record.test_name for record in result["records"]} == {"Case_A", "Case_B", "Case_C"}


def test_runCombinedQuery_queryTextCombinesWithClassFilters():
    """!
    @brief FR-026 text search and FR-028 classification filters apply together (FR-029).
    """
    result = runCombinedQuery(_fixtureRecords(), queryText="Lock", buildId="10")

    assert {record.test_name for record in result["records"]} == {"Case_A", "Case_B", "Case_C", "Case_D"}


def test_runCombinedQuery_failedOnlyWithNoSortKey_usesModuleFunctionTestNameOrder():
    """!
    @brief FR-030's default failed-only ordering is applied when no explicit sortKey is given.
    """
    result = runCombinedQuery(_fixtureRecords(), failedOnly=True)

    # All four FAILED rows share module="ChildLockController"; within that,
    # function "Lock" (Case_A/B/F) sorts before "Unlock" (Case_C), and ties
    # within "Lock" sort by test_name.
    assert [record.test_name for record in result["records"]] == ["Case_A", "Case_B", "Case_F", "Case_C"]


def test_runCombinedQuery_returnsFilterOptionsScopedToSearchedRecords():
    """!
    @brief filterOptions reflects the values available after the text search (FR-028).
    """
    result = runCombinedQuery(_fixtureRecords(), queryText="ChildLockController")

    assert result["filterOptions"]["module"] == ["ChildLockController"]
    assert "Beta" not in result["filterOptions"]["module"]


def test_runCombinedQuery_appliesPaginationOnTheFinalFilteredSet():
    """!
    @brief The page metadata (records/pageSize/totalPages) reflects the fully filtered set (FR-031).
    """
    result = runCombinedQuery(_fixtureRecords(), buildId="10", module="ChildLockController", pageSize=25, page=1)

    assert result["totalMatches"] == 4
    assert result["pageSize"] == 25
    assert result["totalPages"] == 1
    assert len(result["records"]) == 4
