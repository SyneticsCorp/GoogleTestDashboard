"""!
@file test_sorting.py
@brief Unit tests for FR-030 test-list sorting (src/gtestdash/query/sorting.py).
"""
from gtestdash.parsing.models import ResultRecord
from gtestdash.query.sorting import sortRecords


def _makeRecord(module, function, testName, status="PASSED", durationSeconds=0.1, suite=None):
    """!
    @brief Build a minimal ResultRecord for sorting tests.
    @param module Module name to assign.
    @param function tested_function value to assign.
    @param testName test_name to assign.
    @param status Normalized status string.
    @param durationSeconds Duration in seconds.
    @param suite testsuite name; defaults to "{module}.Suite" when omitted.
    @return A ResultRecord with placeholder values for every other field.
    """
    return ResultRecord(
        build_id="10",
        build_timestamp="2026-01-01T00:00:00Z",
        module=module,
        suite=suite or f"{module}.Suite",
        function=function,
        test_name=testName,
        classname=f"{module}.Suite",
        status=status,
        duration_seconds=durationSeconds,
        timestamp=None,
        test_file="widget_test.cc",
        line=1,
        failure_type=None,
        failure_summary=None,
        failure_detail=None,
        source_file=None,
        synthetic_data=None,
    )


def test_sortRecords_byStatus_ordersAlphabeticallyByStatus():
    """!
    @brief sortKey="status" orders records by status string (FR-030).
    """
    passed = _makeRecord("Alpha", "F", "Case_A", status="PASSED")
    failed = _makeRecord("Alpha", "F", "Case_B", status="FAILED")
    error = _makeRecord("Alpha", "F", "Case_C", status="ERROR")

    ordered = sortRecords([passed, failed, error], sortKey="status")

    assert [record.status for record in ordered] == ["ERROR", "FAILED", "PASSED"]


def test_sortRecords_byModule_ordersAlphabeticallyByModule():
    """!
    @brief sortKey="module" orders records by module name (FR-030).
    """
    beta = _makeRecord("Beta", "F", "Case_A")
    alpha = _makeRecord("Alpha", "F", "Case_B")

    ordered = sortRecords([beta, alpha], sortKey="module")

    assert [record.module for record in ordered] == ["Alpha", "Beta"]


def test_sortRecords_byFunctionOrSuite_ordersByFunctionField():
    """!
    @brief sortKey="functionOrSuite" orders records by their function name (FR-030).
    """
    lock = _makeRecord("Alpha", "Lock", "Case_A")
    unlock = _makeRecord("Alpha", "Unlock", "Case_B")

    ordered = sortRecords([unlock, lock], sortKey="functionOrSuite")

    assert [record.function for record in ordered] == ["Lock", "Unlock"]


def test_sortRecords_byTestName_ordersAlphabeticallyByTestName():
    """!
    @brief sortKey="testName" orders records by test_name (FR-030).
    """
    caseB = _makeRecord("Alpha", "F", "Case_B")
    caseA = _makeRecord("Alpha", "F", "Case_A")

    ordered = sortRecords([caseB, caseA], sortKey="testName")

    assert [record.test_name for record in ordered] == ["Case_A", "Case_B"]


def test_sortRecords_byDuration_ordersFastestFirst():
    """!
    @brief sortKey="duration" orders records by duration_seconds ascending (FR-030).
    """
    slow = _makeRecord("Alpha", "F", "Case_A", durationSeconds=0.9)
    fast = _makeRecord("Alpha", "F", "Case_B", durationSeconds=0.1)

    ordered = sortRecords([slow, fast], sortKey="duration")

    assert [record.test_name for record in ordered] == ["Case_B", "Case_A"]


def test_sortRecords_noSortKeyNoFailedOnly_preservesOriginalOrder():
    """!
    @brief With neither sortKey nor failedOnly, the input order is preserved unchanged.
    """
    records = [_makeRecord("Beta", "F", "Case_A"), _makeRecord("Alpha", "F", "Case_B")]

    ordered = sortRecords(records)

    assert [record.test_name for record in ordered] == ["Case_A", "Case_B"]


def test_sortRecords_failedOnlyDefault_ordersByModuleThenFunctionThenTestName():
    """!
    @brief FR-030 default failed-only ordering: module, then function/suite, then test name.
    """
    betaLock = _makeRecord("Beta", "Lock", "Case_Z", status="FAILED")
    alphaUnlock = _makeRecord("Alpha", "Unlock", "Case_B", status="FAILED")
    alphaLockB = _makeRecord("Alpha", "Lock", "Case_B", status="FAILED")
    alphaLockA = _makeRecord("Alpha", "Lock", "Case_A", status="FAILED")

    ordered = sortRecords([betaLock, alphaUnlock, alphaLockB, alphaLockA], failedOnly=True)

    assert [record.test_name for record in ordered] == ["Case_A", "Case_B", "Case_B", "Case_Z"]
    assert [record.module for record in ordered] == ["Alpha", "Alpha", "Alpha", "Beta"]


def test_sortRecords_isStable_tiedKeysKeepOriginalRelativeOrder():
    """!
    @brief FR-030 acceptance: identical sort keys never get reordered between calls (stable sort).
    """
    first = _makeRecord("Alpha", "F", "Case_A", durationSeconds=0.5)
    second = _makeRecord("Alpha", "F", "Case_A", durationSeconds=0.1)
    records = [first, second]

    orderedByModule = sortRecords(records, sortKey="module")
    orderedAgain = sortRecords(records, sortKey="module")

    assert orderedByModule == [first, second]
    assert orderedAgain == [first, second]
