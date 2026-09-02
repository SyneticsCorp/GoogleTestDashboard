"""!
@file test_healthz_smoke.py
@brief Phase 0 Playwright scaffolding smoke test.

Proves the live-server + browser fixtures in tests/e2e/conftest.py work end
to end. Later phases replace/extend this with cases transcribed from
TestCase_Template.xlsx by tdd-flow.
"""
import json

import pytest


@pytest.mark.e2e
def test_healthzPage_showsOkStatusInBrowser(page, liveServerUrl):
    """!
    @brief A real browser can load the health-check route served by a live
           Flask server and read back its JSON body.
    """
    response = page.goto(f"{liveServerUrl}/healthz")

    assert response.status == 200
    bodyText = page.inner_text("body")
    assert json.loads(bodyText) == {"status": "ok"}
