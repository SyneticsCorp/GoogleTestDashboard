"""!
@file builds.py
@brief Build-detail route: GET /builds/<build_id> (FR-018, FR-019).
"""
from flask import abort, render_template

from gtestdash.aggregation.build_history import summarizeBuildsByBuild
from gtestdash.aggregation.grouping import numericBuildIdSortKey
from gtestdash.aggregation.module_distribution import computeModuleDistribution
from gtestdash.web.routes.route_helpers import buildTestDetailUrl


def _findBuildSummary(buildSummaries, buildId):
    """!
    @brief Look up one build's summary by id among all summaries.
    @param buildSummaries Per-build summaries, as returned by summarizeBuildsByBuild().
    @param buildId Build id to look for.
    @return The matching summary dict, or None when buildId is unknown (FR-018).
    """
    return next((summary for summary in buildSummaries if summary["buildId"] == buildId), None)


def _resolvePrevNextBuildIds(buildSummaries, buildId):
    """!
    @brief Determine the numerically-previous and -next build ids for navigation (FR-018).
    @param buildSummaries Per-build summaries, ascending by build id (see
           build_history.summarizeBuildsByBuild()).
    @param buildId The currently-viewed build id, assumed present.
    @return Tuple (prevBuildId, nextBuildId); either is None at the first/last build.
    """
    orderedIds = sorted((summary["buildId"] for summary in buildSummaries), key=numericBuildIdSortKey)
    index = orderedIds.index(buildId)
    prevBuildId = orderedIds[index - 1] if index > 0 else None
    nextBuildId = orderedIds[index + 1] if index < len(orderedIds) - 1 else None
    return prevBuildId, nextBuildId


def _toTestRow(record):
    """!
    @brief Project one ResultRecord into the fields FR-019's full test table needs.
    @param record A ResultRecord belonging to the viewed build.
    @return Dict with status, module, function, suite, testName, durationSeconds,
            testFile, line and testUrl.
    """
    return {
        "status": record.status,
        "module": record.module,
        "function": record.function,
        "suite": record.suite,
        "testName": record.test_name,
        "durationSeconds": record.duration_seconds,
        "testFile": record.test_file,
        "line": record.line,
        "testUrl": buildTestDetailUrl(record),
    }


def buildBuildDetailContext(records, buildId):
    """!
    @brief Assemble every value build_detail.html needs for one build (FR-018, FR-019).
    @param records Full list of ResultRecord across every build.
    @param buildId Build id requested via the route (a str, e.g. "10").
    @return Dict of template context (buildSummary, moduleDistribution, testRows,
            prevBuildId, nextBuildId), or None when buildId is not present
            among records, signaling the route should 404.
    """
    buildSummaries = summarizeBuildsByBuild(records)
    buildSummary = _findBuildSummary(buildSummaries, buildId)
    if buildSummary is None:
        return None

    prevBuildId, nextBuildId = _resolvePrevNextBuildIds(buildSummaries, buildId)
    buildRecords = [record for record in records if record.build_id == buildId]

    return {
        "buildSummary": buildSummary,
        "moduleDistribution": computeModuleDistribution(records, buildId),
        "testRows": [_toTestRow(record) for record in buildRecords],
        "prevBuildId": prevBuildId,
        "nextBuildId": nextBuildId,
    }


def registerBuildDetailRoute(app):
    """!
    @brief Register GET /builds/<build_id> on the given Flask app (FR-018, FR-019).
    @param app Flask application instance to attach the route to.
    """

    @app.get("/builds/<build_id>")
    def buildDetail(build_id):
        """!
        @brief Render one build's detail page from the app's currently loaded snapshot.
        @param build_id Build id path segment, e.g. "10".
        @return Rendered build_detail.html, or a 404 for an unknown build id.
        """
        snapshot = app.config["SNAPSHOT"]
        context = buildBuildDetailContext(snapshot.records, build_id)
        if context is None:
            abort(404)
        return render_template("build_detail.html", **context)
