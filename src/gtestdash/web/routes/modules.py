"""!
@file modules.py
@brief Module-detail route: GET /builds/<build_id>/modules/<module> (FR-020, FR-021).
"""
from flask import abort, render_template, request

from gtestdash.aggregation.build_summary import computeCounts, computeFailureRate
from gtestdash.aggregation.module_trend import computeModuleTrendAcrossBuilds
from gtestdash.web.routes.route_helpers import buildTestDetailUrl


def _toTestRow(record):
    """!
    @brief Project one ResultRecord into the fields FR-021's module test table needs.
    @param record A ResultRecord belonging to the viewed build and module.
    @return Dict with status, function, suite, testName, durationSeconds,
            testFile, line and testUrl.
    """
    return {
        "status": record.status,
        "function": record.function,
        "suite": record.suite,
        "testName": record.test_name,
        "durationSeconds": record.duration_seconds,
        "testFile": record.test_file,
        "line": record.line,
        "testUrl": buildTestDetailUrl(record),
    }


def _summarizeModule(moduleRecords, buildId, module):
    """!
    @brief Fold one build+module's records into FR-020's summary metrics.
    @param moduleRecords ResultRecord list already scoped to one build and module.
    @param buildId Build id these records belong to.
    @param module Module name these records belong to.
    @return Dict with buildId, module, total/passed/failed/error/skipped,
            failureRate and durationSeconds.
    """
    counts = computeCounts(moduleRecords)
    return {
        "buildId": buildId,
        "module": module,
        "total": counts["total"],
        "passed": counts["passed"],
        "failed": counts["failed"],
        "error": counts["error"],
        "skipped": counts["skipped"],
        "failureRate": computeFailureRate(counts),
        "durationSeconds": round(sum(record.duration_seconds for record in moduleRecords), 3),
    }


def _applyListFilters(moduleRecords, functionFilter, suiteFilter):
    """!
    @brief Apply the simple function/suite equality filters ahead of Phase 5's shared query engine (FR-021).
    @param moduleRecords ResultRecord list already scoped to one build and module.
    @param functionFilter Exact function name to keep, or None/empty for no filter.
    @param suiteFilter Exact suite name to keep, or None/empty for no filter.
    @return Filtered ResultRecord list.
    """
    filtered = moduleRecords
    if functionFilter:
        filtered = [record for record in filtered if record.function == functionFilter]
    if suiteFilter:
        filtered = [record for record in filtered if record.suite == suiteFilter]
    return filtered


def buildModuleDetailContext(records, buildId, module, functionFilter=None, suiteFilter=None):
    """!
    @brief Assemble every value module_detail.html needs for one build+module (FR-020, FR-021).
    @param records Full list of ResultRecord across every build.
    @param buildId Build id requested via the route (a str, e.g. "10").
    @param module Module name requested via the route.
    @param functionFilter Optional exact function name to restrict testRows to (FR-021).
    @param suiteFilter Optional exact suite name to restrict testRows to (FR-021).
    @return Dict of template context (moduleSummary, moduleTrend, testRows), or
            None when the build+module combination is not present among
            records, signaling the route should 404.
    """
    moduleRecords = [record for record in records if record.build_id == buildId and record.module == module]
    if not moduleRecords:
        return None

    filteredRecords = _applyListFilters(moduleRecords, functionFilter, suiteFilter)

    return {
        "moduleSummary": _summarizeModule(moduleRecords, buildId, module),
        "moduleTrend": computeModuleTrendAcrossBuilds(records, module),
        "testRows": [_toTestRow(record) for record in filteredRecords],
        "functionFilter": functionFilter,
        "suiteFilter": suiteFilter,
    }


def registerModuleDetailRoute(app):
    """!
    @brief Register GET /builds/<build_id>/modules/<module> on the given Flask app (FR-020, FR-021).
    @param app Flask application instance to attach the route to.
    """

    @app.get("/builds/<build_id>/modules/<module>")
    def moduleDetail(build_id, module):
        """!
        @brief Render one build+module's detail page from the app's currently loaded snapshot.
        @param build_id Build id path segment, e.g. "10".
        @param module Module name path segment, e.g. "ChildLockController".
        @return Rendered module_detail.html, or a 404 for an unknown combination.
        """
        snapshot = app.config["SNAPSHOT"]
        functionFilter = request.args.get("function") or None
        suiteFilter = request.args.get("suite") or None
        context = buildModuleDetailContext(snapshot.records, build_id, module, functionFilter, suiteFilter)
        if context is None:
            abort(404)
        return render_template("module_detail.html", **context)
