"""!
@file test_modules_route.py
@brief Unit tests for the module-detail context builder (src/gtestdash/web/routes/modules.py, FR-020/021).
"""
from gtestdash.parsing.models import ResultRecord
from gtestdash.web.routes.modules import buildModuleDetailContext


def _makeRecord(buildId, module, status, function, suite, testName):
    """!
    @brief Build a minimal ResultRecord for module-detail context tests.
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
        duration_seconds=0.3,
        timestamp=None,
        test_file="widget_test.cc",
        line=7,
        failure_type=None,
        failure_summary=None,
        failure_detail=None,
        source_file=None,
        synthetic_data=None,
    )


def _mixedModuleAndBuildRecords():
    """!
    @brief Build "01"/"02" x module "Alpha"/"Beta", "Alpha" split across two functions/suites.
    @return Flat ResultRecord list for build/module scoping and filter tests.
    """
    return [
        _makeRecord("01", "Alpha", "PASSED", "Lock", "Alpha.LockSuite", "Case_A"),
        _makeRecord("01", "Alpha", "FAILED", "Unlock", "Alpha.UnlockSuite", "Case_B"),
        _makeRecord("01", "Beta", "PASSED", "Sense", "Beta.SenseSuite", "Case_C"),
        _makeRecord("02", "Alpha", "PASSED", "Lock", "Alpha.LockSuite", "Case_A"),
    ]


def test_buildModuleDetailContext_unknownBuildId_returnsNone():
    """!
    @brief An unknown build id yields None so the route can 404 (FR-020).
    """
    context = buildModuleDetailContext(_mixedModuleAndBuildRecords(), "99", "Alpha")

    assert context is None


def test_buildModuleDetailContext_unknownModuleForKnownBuild_returnsNone():
    """!
    @brief A module absent from the given build yields None so the route can 404 (FR-020).
    """
    context = buildModuleDetailContext(_mixedModuleAndBuildRecords(), "02", "Beta")

    assert context is None


def test_buildModuleDetailContext_summary_countsOnlyThatBuildAndModule():
    """!
    @brief moduleSummary reflects only the requested build+module's records (FR-020).
    """
    context = buildModuleDetailContext(_mixedModuleAndBuildRecords(), "01", "Alpha")

    assert context["moduleSummary"]["total"] == 2
    assert context["moduleSummary"]["failed"] == 1
    assert context["moduleSummary"]["failureRate"] == 50.0


def test_buildModuleDetailContext_trend_coversModuleAcrossAllItsBuilds():
    """!
    @brief moduleTrend is not limited to the viewed build; it spans every build with that module (FR-020).
    """
    context = buildModuleDetailContext(_mixedModuleAndBuildRecords(), "01", "Alpha")

    assert [point["buildId"] for point in context["moduleTrend"]] == ["01", "02"]


def test_buildModuleDetailContext_testRows_scopedToBuildAndModuleOnly():
    """!
    @brief testRows excludes other modules and other builds (FR-021).
    """
    context = buildModuleDetailContext(_mixedModuleAndBuildRecords(), "01", "Alpha")

    assert {row["testName"] for row in context["testRows"]} == {"Case_A", "Case_B"}


def test_buildModuleDetailContext_functionFilter_restrictsToMatchingFunction():
    """!
    @brief A functionFilter keeps only rows whose function matches (FR-021).
    """
    context = buildModuleDetailContext(_mixedModuleAndBuildRecords(), "01", "Alpha", functionFilter="Lock")

    assert {row["testName"] for row in context["testRows"]} == {"Case_A"}


def test_buildModuleDetailContext_suiteFilter_restrictsToMatchingSuite():
    """!
    @brief A suiteFilter keeps only rows whose suite matches (FR-021).
    """
    context = buildModuleDetailContext(_mixedModuleAndBuildRecords(), "01", "Alpha", suiteFilter="Alpha.UnlockSuite")

    assert {row["testName"] for row in context["testRows"]} == {"Case_B"}


def test_buildModuleDetailContext_noFilter_includesEveryTestInThatBuildAndModule():
    """!
    @brief With no filter, every one of the build+module's tests is listed (FR-021 acceptance shape).
    """
    context = buildModuleDetailContext(_mixedModuleAndBuildRecords(), "01", "Alpha")

    assert len(context["testRows"]) == 2
