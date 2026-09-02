"""!
@file test_text_search.py
@brief Unit tests for FR-026 case-insensitive substring search (src/gtestdash/query/text_search.py).
"""
from gtestdash.parsing.models import ResultRecord
from gtestdash.query.text_search import searchRecords


def _makeRecord(
    module="Mod",
    suite="Mod.Suite",
    function="Func",
    testName="Case_One",
    classname="Mod.Suite",
    testFile="widget_test.cc",
    sourceFile="widget.cc",
    failureSummary=None,
    failureDetail=None,
):
    """!
    @brief Build a ResultRecord exercising every FR-026 searchable field.
    @param module property[name=module] value.
    @param suite testsuite name.
    @param function tested_function value.
    @param testName testcase name.
    @param classname testcase classname.
    @param testFile testcase file.
    @param sourceFile source_file property value.
    @param failureSummary failure@message value, or None.
    @param failureDetail failure body text, or None.
    @return A ResultRecord with placeholder values for every other field.
    """
    return ResultRecord(
        build_id="10",
        build_timestamp="2026-01-01T00:00:00Z",
        module=module,
        suite=suite,
        function=function,
        test_name=testName,
        classname=classname,
        status="PASSED",
        duration_seconds=0.1,
        timestamp=None,
        test_file=testFile,
        line=1,
        failure_type=None,
        failure_summary=failureSummary,
        failure_detail=failureDetail,
        source_file=sourceFile,
        synthetic_data=None,
    )


def test_searchRecords_emptyQuery_returnsEveryRecordUnchanged():
    """!
    @brief A falsy queryText ("" or None) returns every record, e.g. for "reset" (FR-029).
    """
    records = [_makeRecord(), _makeRecord(module="Other")]

    assert searchRecords(records, "") == records
    assert searchRecords(records, None) == records


def test_searchRecords_matchesByModule_caseInsensitive():
    """!
    @brief A module-name substring matches regardless of case (FR-026).
    """
    target = _makeRecord(module="ChildLockController")
    other = _makeRecord(module="SpeedInterlock")

    found = searchRecords([target, other], "childlock")

    assert found == [target]


def test_searchRecords_matchesByFunctionAndTestName():
    """!
    @brief FR-026 acceptance: searching "EvaluateLockRequest" finds that function and test name.
    """
    byFunction = _makeRecord(function="EvaluateLockRequest", testName="Case_A")
    byTestName = _makeRecord(function="Other", testName="EvaluateLockRequest_Handles_Timeout")
    unrelated = _makeRecord(function="Unrelated", testName="Case_B")

    found = searchRecords([byFunction, byTestName, unrelated], "EvaluateLockRequest")

    assert found == [byFunction, byTestName]


def test_searchRecords_matchesBySuiteClassnameFilesAndFailureText():
    """!
    @brief FR-026 covers suite, classname, test file, source file and failure summary/detail.
    """
    bySuite = _makeRecord(suite="Alpha.LockSuite")
    byClassname = _makeRecord(classname="Beta.SenseSuite")
    byTestFile = _makeRecord(testFile="lock_actuator_test.cc")
    bySourceFile = _makeRecord(sourceFile="lock_actuator.cc")
    byFailureSummary = _makeRecord(failureSummary="Expected true, actual false")
    byFailureDetail = _makeRecord(failureDetail="Expected: true\nActual: false")

    for target, needle in (
        (bySuite, "LockSuite"),
        (byClassname, "SenseSuite"),
        (byTestFile, "lock_actuator_test"),
        (bySourceFile, "lock_actuator.cc"),
        (byFailureSummary, "actual false"),
        (byFailureDetail, "Actual: false"),
    ):
        assert searchRecords([target], needle) == [target]


def test_searchRecords_noMatch_returnsEmptyList():
    """!
    @brief A query matching nothing returns an empty list rather than raising.
    """
    records = [_makeRecord(), _makeRecord(module="Other")]

    assert searchRecords(records, "NoSuchTextAnywhere") == []


def test_searchRecords_toleratesRecordsWithNoneFailureFields():
    """!
    @brief Records with no failure info (PASSED tests) are not errors during search (FR-024 interplay).
    """
    record = _makeRecord(failureSummary=None, failureDetail=None)

    assert searchRecords([record], "childlock") == []
    assert searchRecords([record], "") == [record]
