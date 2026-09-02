"""!
@file test_route_helpers.py
@brief Unit tests for shared route helpers (src/gtestdash/web/routes/route_helpers.py).
"""
from gtestdash.parsing.models import ResultRecord
from gtestdash.web.routes.route_helpers import (
    attachPageNavLinks,
    buildListPageUrl,
    buildTestDetailUrl,
    findRecordByTestId,
    readListQueryArgs,
)


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


def test_findRecordByTestId_matchesRecordWithSameBuildClassnameAndTestName():
    """!
    @brief findRecordByTestId() is the reverse of buildTestDetailUrl()'s slug (FR-022).
    """
    target = _makeRecord("10", "ChildLockController.Suite", "Locks_WhenChildLockActive")
    other = _makeRecord("10", "ChildLockController.Suite", "OtherTest")

    found = findRecordByTestId([other, target], "10", "ChildLockController.Suite.Locks_WhenChildLockActive")

    assert found is target


def test_findRecordByTestId_ignoresRecordsFromOtherBuilds():
    """!
    @brief A matching classname.test_name in a different build is not returned (FR-022).
    """
    wrongBuild = _makeRecord("09", "ChildLockController.Suite", "Locks_WhenChildLockActive")

    found = findRecordByTestId([wrongBuild], "10", "ChildLockController.Suite.Locks_WhenChildLockActive")

    assert found is None


def test_findRecordByTestId_unknownTestId_returnsNone():
    """!
    @brief An unknown test_id yields None so the route can 404 (FR-022).
    """
    record = _makeRecord("10", "ChildLockController.Suite", "Locks_WhenChildLockActive")

    found = findRecordByTestId([record], "10", "NoSuchClass.NoSuchTest")

    assert found is None


def test_buildListPageUrl_noCurrentArgsNoOverrides_returnsBarePath():
    """!
    @brief With no query state at all, the URL is just the bare path (FR-031 base case).
    """
    url = buildListPageUrl("/builds/10", {})

    assert url == "/builds/10"


def test_buildListPageUrl_appliesOverridesOnTopOfCurrentArgs():
    """!
    @brief An override (e.g. changing the page) is merged over the current query args (FR-031).
    """
    url = buildListPageUrl("/builds/10", {"q": "Lock", "page": "1"}, page=2)

    assert url == "/builds/10?q=Lock&page=2"


def test_buildListPageUrl_noneOverride_removesThatKey():
    """!
    @brief Passing None for a key removes it, e.g. clearing a filter (FR-029 "전체 초기화" building block).
    """
    url = buildListPageUrl("/builds/10", {"q": "Lock", "status": "FAILED"}, status=None)

    assert url == "/builds/10?q=Lock"


def test_attachPageNavLinks_middlePage_setsBothPrevAndNextUrls():
    """!
    @brief A middle page gets both a prevPageUrl and a nextPageUrl (FR-031).
    """
    context = {"page": 2, "totalPages": 3}

    attachPageNavLinks(context, "/builds/10", {})

    assert context["prevPageUrl"] == "/builds/10?page=1"
    assert context["nextPageUrl"] == "/builds/10?page=3"


def test_attachPageNavLinks_firstPage_hasNoPrevUrl():
    """!
    @brief The first page's prevPageUrl is None (FR-031, mirrors FR-018's build nav).
    """
    context = {"page": 1, "totalPages": 3}

    attachPageNavLinks(context, "/builds/10", {})

    assert context["prevPageUrl"] is None
    assert context["nextPageUrl"] == "/builds/10?page=2"


def test_attachPageNavLinks_lastPage_hasNoNextUrl():
    """!
    @brief The last page's nextPageUrl is None (FR-031).
    """
    context = {"page": 3, "totalPages": 3}

    attachPageNavLinks(context, "/builds/10", {})

    assert context["nextPageUrl"] is None
    assert context["prevPageUrl"] == "/builds/10?page=2"


def test_readListQueryArgs_baseKeys_alwaysPresentWithDefaults():
    """!
    @brief The shared FR-025~031 keys are always read, with sensible defaults when absent.
    """
    parsed = readListQueryArgs({})

    assert parsed == {
        "queryText": None,
        "failedOnly": False,
        "status": None,
        "functionOrSuite": None,
        "sortKey": None,
        "page": 1,
        "pageSize": 50,
    }


def test_readListQueryArgs_parsesEveryValueWhenPresent():
    """!
    @brief Every FR-025~031 query param is read into its context-builder keyword.
    """
    args = {
        "q": "Lock",
        "failedOnly": "true",
        "status": "FAILED",
        "functionOrSuite": "EvaluateLockRequest",
        "sort": "duration",
        "page": "2",
        "pageSize": "25",
    }

    parsed = readListQueryArgs(args)

    assert parsed["queryText"] == "Lock"
    assert parsed["failedOnly"] is True
    assert parsed["status"] == "FAILED"
    assert parsed["functionOrSuite"] == "EvaluateLockRequest"
    assert parsed["sortKey"] == "duration"
    assert parsed["page"] == 2
    assert parsed["pageSize"] == 25


def test_readListQueryArgs_includeBuildId_addsBuildIdOnlyWhenRequested():
    """!
    @brief buildId is only parsed (and only present in the result) when includeBuildId=True.
    """
    withBuildId = readListQueryArgs({"buildId": "10"}, includeBuildId=True)
    withoutFlag = readListQueryArgs({"buildId": "10"})

    assert withBuildId["buildId"] == "10"
    assert "buildId" not in withoutFlag


def test_readListQueryArgs_includeModule_addsModuleOnlyWhenRequested():
    """!
    @brief module is only parsed (and only present in the result) when includeModule=True.
    """
    withModule = readListQueryArgs({"module": "Alpha"}, includeModule=True)
    withoutFlag = readListQueryArgs({"module": "Alpha"})

    assert withModule["module"] == "Alpha"
    assert "module" not in withoutFlag
