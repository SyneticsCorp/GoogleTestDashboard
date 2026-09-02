"""!
@file modules.py
@brief Module-detail route: GET /builds/<build_id>/modules/<module> (FR-020, FR-021, FR-025~031).
"""
from flask import abort, render_template, request

from gtestdash.aggregation.build_summary import computeCounts, computeFailureRate
from gtestdash.aggregation.module_trend import computeModuleTrendAcrossBuilds
from gtestdash.query.combined_query import runCombinedQuery
from gtestdash.web.routes.route_helpers import applyListPagePresentation, buildTestDetailUrl, readListQueryArgs


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


def buildModuleDetailContext(
    records,
    buildId,
    module,
    queryText=None,
    failedOnly=False,
    status=None,
    functionOrSuite=None,
    sortKey=None,
    page=1,
    pageSize=50,
):
    """!
    @brief Assemble every value module_detail.html needs for one build+module (FR-020, FR-021, FR-025~031).
    @param records Full list of ResultRecord across every build.
    @param buildId Build id requested via the route (a str, e.g. "10").
    @param module Module name requested via the route.
    @param queryText FR-026 free-text search, scoped to this build+module (FR-027).
    @param failedOnly FR-025 failed-only toggle.
    @param status FR-028 exact status filter.
    @param functionOrSuite FR-021/FR-028 exact function-or-suite filter (matches either field).
    @param sortKey FR-030 sort key, or None for the default order.
    @param page FR-031 1-based page number.
    @param pageSize FR-031 page size (25/50/100; other values fall back to 50).
    @return Dict of template context (moduleSummary, moduleTrend, testRows,
            plus the FR-025~031 query/pagination/filter state), or None when
            the build+module combination is not present among records,
            signaling the route should 404.
    """
    moduleRecords = [record for record in records if record.build_id == buildId and record.module == module]
    if not moduleRecords:
        return None

    queryResult = runCombinedQuery(
        records,
        queryText=queryText,
        failedOnly=failedOnly,
        status=status,
        buildId=buildId,
        module=module,
        functionOrSuite=functionOrSuite,
        sortKey=sortKey,
        page=page,
        pageSize=pageSize,
    )

    return {
        "moduleSummary": _summarizeModule(moduleRecords, buildId, module),
        "moduleTrend": computeModuleTrendAcrossBuilds(records, module),
        "testRows": [_toTestRow(record) for record in queryResult["records"]],
        "searchContextBuildId": buildId,
        "queryText": queryText or "",
        "failedOnly": failedOnly,
        "statusFilter": status,
        "functionOrSuiteFilter": functionOrSuite,
        "sortKey": sortKey,
        "page": queryResult["page"],
        "pageSize": queryResult["pageSize"],
        "totalMatches": queryResult["totalMatches"],
        "totalPages": queryResult["totalPages"],
        "displayRange": queryResult["displayRange"],
        "filterOptions": queryResult["filterOptions"],
    }


def registerModuleDetailRoute(app):
    """!
    @brief Register GET /builds/<build_id>/modules/<module> on the given Flask app (FR-020, FR-021, FR-025~031).
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
        queryArgs = readListQueryArgs(request.args)
        context = buildModuleDetailContext(snapshot.records, build_id, module, **queryArgs)
        if context is None:
            abort(404)
        applyListPagePresentation(context, request.path, request.args)
        return render_template("module_detail.html", **context)
