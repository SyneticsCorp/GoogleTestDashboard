"""!
@file app.py
@brief Flask application factory for the GoogleTest dashboard.

Builds the results snapshot once at startup (FR-001~008) and stores it on
app.config["SNAPSHOT"] so every route reads a single consistent snapshot per
request instead of re-parsing the XML tree. POST /refresh (a later phase)
replaces this reference atomically; nothing here mutates it in place.
"""
from flask import Flask, jsonify

from gtestdash.config import resolveResultsPath
from gtestdash.repository import buildSnapshot
from gtestdash.web.routes.dashboard import registerDashboardRoute
from gtestdash.web.template_filters import formatPercent, formatPercentDiff


def createApp(resultsPath=None):
    """!
    @brief Build and configure the Flask application instance.
    @param resultsPath Optional explicit GoogleTest results root; when
           omitted, config.resolveResultsPath() applies its default
           ("GoogleTestResults" under the current working directory) (FR-001).
    @return A configured Flask app exposing GET /healthz and GET / (FR-009~017).
    """
    app = Flask(__name__)
    resolvedPath = resolveResultsPath(resultsPath)
    app.config["SNAPSHOT"] = buildSnapshot(resolvedPath)
    app.jinja_env.filters["percent"] = formatPercent
    app.jinja_env.filters["percentDiff"] = formatPercentDiff
    registerHealthRoute(app)
    registerDashboardRoute(app)
    return app


def registerHealthRoute(app):
    """!
    @brief Register GET /healthz, an infrastructure smoke-check endpoint.
    @param app Flask application instance to attach the route to.
    """

    @app.get("/healthz")
    def healthz():
        """!
        @brief Report that the Flask process is up and serving requests.
        @return A (JSON body, status code) tuple: {"status": "ok"}, 200.
        """
        return jsonify(status="ok"), 200
