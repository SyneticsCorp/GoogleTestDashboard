"""!
@file test_route_helpers.py
@brief Unit tests for shared route helpers (src/gtestdash/web/routes/route_helpers.py).
"""
from gtestdash.parsing.models import ResultRecord
from gtestdash.web.routes.route_helpers import buildTestDetailUrl


def _makeRecord(buildId, classname, testName):
    """!
    @brief Build a minimal ResultRecord for URL-building tests.
    @param buildId build_id to assign.
    @param classname classname to assign.
    @param testName test_name to assign.
    @return A ResultRecord with placeholder values for every other field.
    """
    return ResultRecord(
        build_id=buildId,
        build_timestamp=None,
        module="Mod",
        suite="Mod.Suite",
        function="Func",
        test_name=testName,
        classname=classname,
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


def test_buildTestDetailUrl_joinsBuildClassnameAndTestNameUnderTestsPath():
    """!
    @brief The URL follows /builds/{build_id}/tests/{classname}.{test_name} (Requirements.md §5).
    """
    record = _makeRecord("10", "ChildLockController.Suite", "Locks_WhenChildLockActive")

    url = buildTestDetailUrl(record)

    assert url == "/builds/10/tests/ChildLockController.Suite.Locks_WhenChildLockActive"


def test_buildTestDetailUrl_percentEncodesSlashesInClassname():
    """!
    @brief A classname/test_name pair containing '/' is percent-encoded so it stays one path segment.
    """
    record = _makeRecord("10", "Weird/Class", "Case/Name")

    url = buildTestDetailUrl(record)

    assert url == "/builds/10/tests/Weird%2FClass.Case%2FName"
