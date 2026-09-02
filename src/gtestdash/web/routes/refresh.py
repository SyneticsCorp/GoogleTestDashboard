"""!
@file refresh.py
@brief Result refresh route: POST /refresh (FR-034).

Re-runs the same discovery+parsing pipeline app.py used at startup
(config.resolveResultsPath() + repository.buildSnapshot()) and atomically
swaps app.config["SNAPSHOT"] for the freshly-built one, so build folders
added after startup are recognized without restarting the process.
"""
from flask import redirect, request, url_for

from gtestdash.config import resolveResultsPath
from gtestdash.repository import buildSnapshot


def registerRefreshRoute(app, resultsPath):
    """!
    @brief Register POST /refresh on the given Flask app (FR-034).
    @param app Flask application instance to attach the route to.
    @param resultsPath The GoogleTest results root this app was created with
           (already resolved by config.resolveResultsPath() in the app factory).
    """

    @app.post("/refresh")
    def refresh():
        """!
        @brief Re-scan resultsPath and atomically replace app.config["SNAPSHOT"] (FR-034).
        @return A redirect back to the referring page, or the dashboard when unknown.
        """
        app.config["SNAPSHOT"] = buildSnapshot(resolveResultsPath(resultsPath))
        return redirect(request.referrer or url_for("dashboard"))
