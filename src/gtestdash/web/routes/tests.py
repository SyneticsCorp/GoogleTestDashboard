"""!
@file tests.py
@brief Test-detail route: GET /builds/<build_id>/tests/<test_id> (FR-022~024).
"""
from flask import abort, render_template

from gtestdash.web.routes.route_helpers import findRecordByTestId


def _toTestDetail(record):
    """!
    @brief Project one ResultRecord into every field test_detail.html shows (FR-022~024).
    @param record A ResultRecord to render.
    @return Dict with identity fields (FR-022) plus failureType/failureSummary/
            failureDetail, each None when record carries no failure (FR-024).
    """
    return {
        "buildId": record.build_id,
        "module": record.module,
        "function": record.function,
        "suite": record.suite,
        "testName": record.test_name,
        "classname": record.classname,
        "status": record.status,
        "durationSeconds": record.duration_seconds,
        "timestamp": record.timestamp,
        "testFile": record.test_file,
        "line": record.line,
        "sourceFile": record.source_file,
        "failureType": record.failure_type,
        "failureSummary": record.failure_summary,
        "failureDetail": record.failure_detail,
    }


def buildTestDetailContext(records, buildId, testId):
    """!
    @brief Assemble every value test_detail.html needs for one test (FR-022~024).
    @param records Full list of ResultRecord across every build.
    @param buildId Build id requested via the route (a str, e.g. "10").
    @param testId The "{classname}.{test_name}" slug requested via the route
           (see route_helpers.findRecordByTestId()).
    @return Dict of template context ({"test": {...}, "searchContextBuildId":
            ...}), or None when the build+test_id combination is not present
            among records, signaling the route should 404. searchContextBuildId
            lets the common search form default its scope to this build (FR-027).
    """
    record = findRecordByTestId(records, buildId, testId)
    if record is None:
        return None
    return {"test": _toTestDetail(record), "searchContextBuildId": record.build_id}


def registerTestDetailRoute(app):
    """!
    @brief Register GET /builds/<build_id>/tests/<test_id> on the given Flask app (FR-022~024).
    @param app Flask application instance to attach the route to.
    """

    @app.get("/builds/<build_id>/tests/<test_id>")
    def testDetail(build_id, test_id):
        """!
        @brief Render one test's detail page from the app's currently loaded snapshot.
        @param build_id Build id path segment, e.g. "10".
        @param test_id "{classname}.{test_name}" slug path segment (FR-022).
        @return Rendered test_detail.html, or a 404 for an unknown combination.
        """
        snapshot = app.config["SNAPSHOT"]
        context = buildTestDetailContext(snapshot.records, build_id, test_id)
        if context is None:
            abort(404)
        return render_template("test_detail.html", **context)
