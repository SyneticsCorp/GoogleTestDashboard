"""!
@file test_app_healthz.py
@brief Integration smoke test for the Flask app factory's health-check route.
"""
from gtestdash.web.app import createApp


def test_healthz_returnsOkStatusJson():
    """!
    @brief GET /healthz responds 200 with a JSON status payload, proving the
           app factory wires up a working Flask app (Phase 0 infra smoke test).
    """
    app = createApp()
    client = app.test_client()

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
