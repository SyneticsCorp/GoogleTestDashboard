"""!
@file test_builds_route.py
@brief Unit tests for the build-detail context builder (src/gtestdash/web/routes/builds.py, FR-018/019).
"""
from gtestdash.parsing.models import ResultRecord
from gtestdash.web.routes.builds import buildBuildDetailContext


def _makeRecord(buildId, module, status, testName="Case_One"):
    """!
    @brief Build a minimal ResultRecord for build-detail context tests.
    @param buildId build_id to assign.
    @param module Module name to assign.
    @param status Normalized status string.
    @param testName test_name to assign.
    @return A ResultRecord with placeholder values for every other field.
    """
    return ResultRecord(
        build_id=buildId,
        build_timestamp="2026-01-01T00:00:00Z",
        module=module,
        suite=f"{module}.Suite",
        function="Func",
        test_name=testName,
        classname=f"{module}.Suite",
        status=status,
        duration_seconds=0.25,
        timestamp=None,
        test_file="widget_test.cc",
        line=42,
        failure_type=None,
        failure_summary=None,
        failure_detail=None,
        source_file=None,
        synthetic_data=None,
    )


def _threeBuildRecords():
    """!
    @brief Three builds ("01", "02", "03"), each with two records in module "Alpha".
    @return Flat ResultRecord list for prev/next and scoping tests.
    """
    return [
        _makeRecord("01", "Alpha", "PASSED", "Case_A"),
        _makeRecord("01", "Alpha", "FAILED", "Case_B"),
        _makeRecord("02", "Alpha", "PASSED", "Case_A"),
        _makeRecord("02", "Alpha", "PASSED", "Case_B"),
        _makeRecord("03", "Alpha", "PASSED", "Case_A"),
        _makeRecord("03", "Alpha", "PASSED", "Case_B"),
    ]


def test_buildBuildDetailContext_unknownBuildId_returnsNone():
    """!
    @brief An unknown build id yields None so the route can 404 (FR-018).
    """
    context = buildBuildDetailContext(_threeBuildRecords(), "99")

    assert context is None


def test_buildBuildDetailContext_middleBuild_hasBothPrevAndNextLinks():
    """!
    @brief Build "02" between "01" and "03" gets both prev and next build ids (FR-018).
    """
    context = buildBuildDetailContext(_threeBuildRecords(), "02")

    assert context["prevBuildId"] == "01"
    assert context["nextBuildId"] == "03"


def test_buildBuildDetailContext_firstBuild_hasNoPrevLink():
    """!
    @brief The first build's prevBuildId is None so the "이전" link is disabled (FR-018).
    """
    context = buildBuildDetailContext(_threeBuildRecords(), "01")

    assert context["prevBuildId"] is None
    assert context["nextBuildId"] == "02"


def test_buildBuildDetailContext_lastBuild_hasNoNextLink():
    """!
    @brief The last build's nextBuildId is None so the "다음" link is disabled (FR-018).
    """
    context = buildBuildDetailContext(_threeBuildRecords(), "03")

    assert context["nextBuildId"] is None
    assert context["prevBuildId"] == "02"


def test_buildBuildDetailContext_buildSummary_reflectsOnlyThatBuildsCounts():
    """!
    @brief buildSummary's total/failed reflect only the requested build's records (FR-018).
    """
    context = buildBuildDetailContext(_threeBuildRecords(), "01")

    assert context["buildSummary"]["buildId"] == "01"
    assert context["buildSummary"]["total"] == 2
    assert context["buildSummary"]["failed"] == 1


def test_buildBuildDetailContext_testRows_listsEveryRecordInThatBuildOnly():
    """!
    @brief testRows contains exactly the requested build's records, none from other builds (FR-019).
    """
    context = buildBuildDetailContext(_threeBuildRecords(), "01")

    assert len(context["testRows"]) == 2
    assert {row["testName"] for row in context["testRows"]} == {"Case_A", "Case_B"}


def test_buildBuildDetailContext_testRows_carryTableColumnsFromRequirements():
    """!
    @brief Each row carries status/module/function/suite/testName/durationSeconds/testFile/line (FR-019).
    """
    context = buildBuildDetailContext(_threeBuildRecords(), "01")

    row = next(row for row in context["testRows"] if row["testName"] == "Case_B")
    assert row["status"] == "FAILED"
    assert row["module"] == "Alpha"
    assert row["function"] == "Func"
    assert row["suite"] == "Alpha.Suite"
    assert row["durationSeconds"] == 0.25
    assert row["testFile"] == "widget_test.cc"
    assert row["line"] == 42
    assert row["testUrl"] == "/builds/01/tests/Alpha.Suite.Case_B"


def test_buildBuildDetailContext_moduleDistribution_scopedToThatBuildOnly():
    """!
    @brief moduleDistribution only reflects the requested build, not the whole dataset (FR-018).
    """
    records = _threeBuildRecords() + [_makeRecord("02", "Beta", "FAILED", "Case_C")]

    context = buildBuildDetailContext(records, "01")

    assert {entry["module"] for entry in context["moduleDistribution"]} == {"Alpha"}


def test_buildBuildDetailContext_defaultQueryState_matchesEveryRecordInBuild():
    """!
    @brief With no query args, totalMatches/testRows reflect the whole build (Phase 5 baseline, FR-029).
    """
    context = buildBuildDetailContext(_threeBuildRecords(), "01")

    assert context["totalMatches"] == 2
    assert len(context["testRows"]) == 2
    assert context["queryText"] == ""
    assert context["failedOnly"] is False


def test_buildBuildDetailContext_searchScopedToOtherBuildsAreExcluded():
    """!
    @brief FR-027: build-detail search never returns records from other builds.
    """
    context = buildBuildDetailContext(_threeBuildRecords(), "01", queryText="Case")

    assert context["totalMatches"] == 2
    assert all(row["testName"].startswith("Case") for row in context["testRows"])


def test_buildBuildDetailContext_failedOnly_narrowsToFailedRecords():
    """!
    @brief FR-025: the failed-only toggle keeps only FAILED-status rows.
    """
    context = buildBuildDetailContext(_threeBuildRecords(), "01", failedOnly=True)

    assert context["totalMatches"] == 1
    assert [row["status"] for row in context["testRows"]] == ["FAILED"]


def test_buildBuildDetailContext_filterOptions_onlyIncludeThatBuildsValues():
    """!
    @brief FR-028: filterOptions never surface a module absent from this build's records.
    """
    context = buildBuildDetailContext(_threeBuildRecords(), "01")

    assert context["filterOptions"]["module"] == ["Alpha"]


def test_buildBuildDetailContext_pagination_reflectsRequestedPageAndSize():
    """!
    @brief FR-031: page/pageSize/totalPages are threaded through from the query engine.
    """
    context = buildBuildDetailContext(_threeBuildRecords(), "01", pageSize=25, page=1)

    assert context["pageSize"] == 25
    assert context["totalPages"] == 1
    assert context["displayRange"] == "1-2"
