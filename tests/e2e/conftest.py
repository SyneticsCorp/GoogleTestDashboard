"""!
@file conftest.py
@brief Shared Playwright/Flask fixtures for end-to-end tests (Phase 0 scaffolding).

Starts the real Flask app (via gtestdash.web.app.createApp) in a background
thread on a free localhost port for the duration of the test session, so
Playwright's browser/page fixtures (from pytest-playwright) can drive it
like a real user would.
"""
import socket
import threading
import time
import urllib.error
import urllib.request

import pytest

from gtestdash.web.app import createApp


def findFreePort():
    """!
    @brief Find an unused TCP port on localhost for the test server to bind.
    @return An available port number.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def waitForServerReady(baseUrl, timeoutSeconds=10):
    """!
    @brief Poll /healthz until the live server responds or the timeout elapses.
    @param baseUrl Base URL of the server under test.
    @param timeoutSeconds Maximum time to wait before giving up.
    @throws RuntimeError when the server never becomes reachable in time.
    """
    deadline = time.time() + timeoutSeconds
    lastError = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{baseUrl}/healthz", timeout=0.5):
                return
        except (urllib.error.URLError, ConnectionError) as error:
            lastError = error
            time.sleep(0.1)
    raise RuntimeError(f"Server at {baseUrl} did not become ready: {lastError}")


@pytest.fixture(scope="session")
def liveServerUrl():
    """!
    @brief Run the real Flask app in a background thread for the test session.
    @return Base URL (http://127.0.0.1:<port>) of the running server.
    """
    app = createApp()
    port = findFreePort()
    serverThread = threading.Thread(
        target=lambda: app.run(host="127.0.0.1", port=port, use_reloader=False),
        daemon=True,
    )
    serverThread.start()

    baseUrl = f"http://127.0.0.1:{port}"
    waitForServerReady(baseUrl)
    return baseUrl
