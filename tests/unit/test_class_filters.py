"""!
@file test_class_filters.py
@brief Unit tests for FR-028 status/build/module/function-or-suite filters
       (src/gtestdash/query/class_filters.py).
"""
from gtestdash.parsing.models import ResultRecord
from gtestdash.query.class_filters import applyClassFilters, availableFilterValues


def _makeRecord(buildId, module, status, function, suite, testName="Case_One"):
    """!
    @brief Build a minimal ResultRecord for classification-filter tests.
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
        duration_seconds=0.2,
        timestamp=None,
        test_file="widget_test.cc",
        line=3,
        failure_type=None,
        failure_summary=None,
        failure_detail=None,
        source_file=None,
        synthetic_data=None,
    )


def _mixedRecords():
    """!
    @brief Two builds, two modules, mixed statuses and distinct functions/suites.
    @return Flat ResultRecord list exercising every class_filters dimension.
    """
    return [
        _makeRecord("09", "Alpha", "PASSED", "Lock", "Alpha.LockSuite", "Case_A"),
        _makeRecord("10", "Alpha", "FAILED", "Unlock", "Alpha.UnlockSuite", "Case_B"),
        _makeRecord("10", "Beta", "PASSED", "Sense", "Beta.SenseSuite", "Case_C"),
        _makeRecord("10", "Beta", "ERROR", "Sense", "Beta.SenseSuite", "Case_D"),
    ]


def test_availableFilterValues_onlyIncludesValuesActuallyPresent():
    """!
    @brief No stale/nonexistent module or suite value appears in the filter lists (FR-028).
    """
    options = availableFilterValues(_mixedRecords())

    assert options["module"] == ["Alpha", "Beta"]
    assert "Gamma" not in options["module"]
    assert "NoSuchSuite" not in options["functionOrSuite"]


def test_availableFilterValues_status_listsOnlyPresentStatusesSorted():
    """!
    @brief Status options are exactly the statuses present, sorted (FR-028).
    """
    options = availableFilterValues(_mixedRecords())

    assert options["status"] == ["ERROR", "FAILED", "PASSED"]


def test_availableFilterValues_buildId_isNumericallySorted():
    """!
    @brief Build id options sort numerically ("09" before "10"), not lexicographically.
    """
    options = availableFilterValues(_mixedRecords())

    assert options["buildId"] == ["09", "10"]


def test_availableFilterValues_functionOrSuite_mergesBothFields():
    """!
    @brief functionOrSuite options include both function and suite values (FR-021/FR-028).
    """
    options = availableFilterValues(_mixedRecords())

    assert "Lock" in options["functionOrSuite"]
    assert "Alpha.LockSuite" in options["functionOrSuite"]


def test_availableFilterValues_emptyRecords_yieldsEmptyLists():
    """!
    @brief An empty result set yields empty filter option lists, not an error (FR-036).
    """
    options = availableFilterValues([])

    assert options == {"status": [], "buildId": [], "module": [], "functionOrSuite": []}


def test_applyClassFilters_noFilters_returnsEveryRecord():
    """!
    @brief No filters supplied returns records unchanged, e.g. for "전체 초기화" (FR-029).
    """
    records = _mixedRecords()

    assert applyClassFilters(records) == records


def test_applyClassFilters_status_keepsOnlyThatStatus():
    """!
    @brief A status filter keeps only records with that exact status (FR-028).
    """
    filtered = applyClassFilters(_mixedRecords(), status="FAILED")

    assert [record.test_name for record in filtered] == ["Case_B"]


def test_applyClassFilters_functionOrSuite_matchesEitherField():
    """!
    @brief functionOrSuite matches a record whose function OR suite equals the value (FR-021, FR-028).
    """
    byFunction = applyClassFilters(_mixedRecords(), functionOrSuite="Lock")
    bySuite = applyClassFilters(_mixedRecords(), functionOrSuite="Beta.SenseSuite")

    assert [record.test_name for record in byFunction] == ["Case_A"]
    assert {record.test_name for record in bySuite} == {"Case_C", "Case_D"}


def test_applyClassFilters_combinesBuildModuleAndFailedOnlyStatus():
    """!
    @brief FR-029 acceptance: build 10 + module Beta + status ERROR narrows to one record.
    """
    filtered = applyClassFilters(_mixedRecords(), buildId="10", module="Beta", status="ERROR")

    assert [record.test_name for record in filtered] == ["Case_D"]
