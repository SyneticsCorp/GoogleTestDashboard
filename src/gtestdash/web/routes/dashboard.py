"""!
@file dashboard.py
@brief Main dashboard route: GET / (FR-009~017).
"""
from flask import render_template, request

from gtestdash.aggregation.build_diff import computeBuildDiff
from gtestdash.aggregation.build_history import summarizeBuildsByBuild
from gtestdash.aggregation.latest_build import resolveLatestBuild
from gtestdash.aggregation.module_distribution import computeModuleDistribution
from gtestdash.aggregation.trend import buildFailureRateTrend
from gtestdash.web.routes.route_helpers import buildTestDetailUrl


def _splitLatestAndPrevious(buildSummaries):
    """!
    @brief Pick the latest build summary and the one immediately before it (FR-009, FR-011).
    @param buildSummaries Per-build summaries, ascending by build id (see
           build_history.summarizeBuildsByBuild()).
    @return Tuple (latestSummary, previousSummary); both None when
            buildSummaries is empty, previousSummary is None when the latest
            build is also the first one.
    """
    if not buildSummaries:
        return None, None

    latestSummary = resolveLatestBuild(buildSummaries)
    orderedIds = [summary["buildId"] for summary in buildSummaries]
    latestIndex = orderedIds.index(latestSummary["buildId"])
    previousSummary = buildSummaries[latestIndex - 1] if latestIndex > 0 else None
    return latestSummary, previousSummary


def _toFailureRow(record):
    """!
    @brief Project one failing ResultRecord into the fields FR-016's list needs.
    @param record A FAILED-status ResultRecord from the latest build.
    @return Dict with module, function, suite, testName, failureSummary,
            testFile, line, durationSeconds and testUrl.
    """
    return {
        "module": record.module,
        "function": record.function,
        "suite": record.suite,
        "testName": record.test_name,
        "failureSummary": record.failure_summary,
        "testFile": record.test_file,
        "line": record.line,
        "durationSeconds": record.duration_seconds,
        "testUrl": buildTestDetailUrl(record),
    }


def _latestFailureRows(records, latestSummary):
    """!
    @brief Build FR-016's latest-failures list from the latest build's records.
    @param records Full record list across every build.
    @param latestSummary Latest build's summary dict, or None when there is no data.
    @return List of failure-row dicts (see _toFailureRow()) for the latest
            build's FAILED records; empty when there is no latest build.
    """
    if latestSummary is None:
        return []
    latestBuildId = latestSummary["buildId"]
    return [
        _toFailureRow(record)
        for record in records
        if record.build_id == latestBuildId and record.status == "FAILED"
    ]


def _resolveLatestSummaryAndDiff(buildSummaries):
    """!
    @brief Resolve the latest build summary together with its diff (FR-009, FR-011).
    @param buildSummaries Per-build summaries, ascending by build id.
    @return Tuple (latestSummary, buildDiff); both None when buildSummaries is empty.
    """
    latestSummary, previousSummary = _splitLatestAndPrevious(buildSummaries)
    if latestSummary is None:
        return None, None
    return latestSummary, computeBuildDiff(latestSummary, previousSummary)


def buildDashboardContext(records, moduleScope="latest"):
    """!
    @brief Assemble every value dashboard.html needs from the raw record list (FR-009~017).
    @param records Full list of ResultRecord across every build.
    @param moduleScope "latest" (default), "cumulative", or a specific build id
           string, selecting the module failure chart's range (FR-014).
    @return Dict of template context: latestSummary, buildDiff, trendPoints,
            moduleScope, moduleDistribution, latestFailures, buildHistory.
    """
    buildSummaries = summarizeBuildsByBuild(records)
    latestSummary, buildDiff = _resolveLatestSummaryAndDiff(buildSummaries)

    return {
        "latestSummary": latestSummary,
        "buildDiff": buildDiff,
        "trendPoints": buildFailureRateTrend(buildSummaries),
        "moduleScope": moduleScope,
        "moduleDistribution": computeModuleDistribution(records, moduleScope),
        "latestFailures": _latestFailureRows(records, latestSummary),
        "buildHistory": list(reversed(buildSummaries)),
    }


def registerDashboardRoute(app):
    """!
    @brief Register GET / on the given Flask app (FR-009~017).
    @param app Flask application instance to attach the route to.
    """

    @app.get("/")
    def dashboard():
        """!
        @brief Render the main dashboard from the app's currently loaded snapshot.
        @return Rendered dashboard.html.
        """
        moduleScope = request.args.get("scope", "latest")
        snapshot = app.config["SNAPSHOT"]
        context = buildDashboardContext(snapshot.records, moduleScope)
        return render_template("dashboard.html", **context)
