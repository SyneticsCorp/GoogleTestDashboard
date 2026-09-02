"""!
@file app.py
@brief Flask application factory for the GoogleTest dashboard (Phase 0 skeleton).

Only infrastructure exists at this stage: an app factory and a health-check
route used to prove the web layer, pytest and Playwright wiring all work.
Dashboard/build/module/test routes are added in later phases.
"""
from flask import Flask, jsonify


def createApp():
    """!
    @brief Build and configure the Flask application instance.
    @return A configured Flask app exposing GET /healthz.
    """
    app = Flask(__name__)
    registerHealthRoute(app)
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
