"""!
@file search.py
@brief Search-results route: GET /search (FR-026~031).
"""
from flask import render_template, request

from gtestdash.query.combined_query import runCombinedQuery
from gtestdash.web.routes.route_helpers import applyListPagePresentation, buildTestDetailUrl, readListQueryArgs


def _toTestRow(record):
    """!
    @brief Project one ResultRecord into the fields the search results table needs.
    @param record A ResultRecord matched by the current query.
    @return Dict with status, buildId, module, function, suite, testName,
            durationSeconds, testFile, line and testUrl.
    """
    return {
        "status": record.status,
        "buildId": record.build_id,
        "module": record.module,
        "function": record.function,
        "suite": record.suite,
        "testName": record.test_name,
        "durationSeconds": record.duration_seconds,
        "testFile": record.test_file,
        "line": record.line,
        "testUrl": buildTestDetailUrl(record),
    }


def buildSearchResultsContext(records, queryArgs):
    """!
    @brief Assemble every value search_results.html needs (FR-026~031).
    @param records Full list of ResultRecord across every build.
    @param queryArgs Dict as returned by route_helpers.readListQueryArgs()
           (called with includeBuildId=True, includeModule=True).
    @return Dict of template context: testRows plus the shared query/
            pagination/filter state (queryText, failedOnly, statusFilter,
            buildIdFilter, moduleFilter, functionOrSuiteFilter, sortKey,
            page, pageSize, totalMatches, totalPages, displayRange,
            filterOptions).
    """
    queryResult = runCombinedQuery(records, **queryArgs)

    return {
        "testRows": [_toTestRow(record) for record in queryResult["records"]],
        "queryText": queryArgs["queryText"] or "",
        "failedOnly": queryArgs["failedOnly"],
        "statusFilter": queryArgs["status"],
        "buildIdFilter": queryArgs["buildId"],
        "moduleFilter": queryArgs["module"],
        "functionOrSuiteFilter": queryArgs["functionOrSuite"],
        "sortKey": queryArgs["sortKey"],
        "page": queryResult["page"],
        "pageSize": queryResult["pageSize"],
        "totalMatches": queryResult["totalMatches"],
        "totalPages": queryResult["totalPages"],
        "displayRange": queryResult["displayRange"],
        "filterOptions": queryResult["filterOptions"],
    }


def registerSearchRoute(app):
    """!
    @brief Register GET /search on the given Flask app (FR-026~031).
    @param app Flask application instance to attach the route to.
    """

    @app.get("/search")
    def searchResults():
        """!
        @brief Render the search-results page from the app's currently loaded snapshot.
        @return Rendered search_results.html.
        """
        snapshot = app.config["SNAPSHOT"]
        queryArgs = readListQueryArgs(request.args, includeBuildId=True, includeModule=True)
        context = buildSearchResultsContext(snapshot.records, queryArgs)
        applyListPagePresentation(context, request.path, request.args)
        return render_template("search_results.html", **context)
