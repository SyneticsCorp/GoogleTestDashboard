"""!
@file conftest.py
@brief Shared Playwright/Flask fixtures for end-to-end tests.

Starts a Flask app (via gtestdash.web.app.createApp) in a background thread
on a free localhost port, so Playwright's browser/page fixtures (from
pytest-playwright) can drive it like a real user would. liveServerUrl (the
real GoogleTestResults dataset, started once per session) is the fixture
almost every test file uses; corruptedXmlServerUrl and
statusPriorityServerUrl start their own per-test server against a synthetic
edge-case tree, for the handful of FR-006/FR-035 cases the real dataset
cannot exercise on its own (see tests/fixtures/edge_cases/).
"""
import os
import shutil
import socket
import threading
import time
import urllib.error
import urllib.request

import pytest

from gtestdash.web.app import createApp

## Real, read-only dataset root; copied into tmp_path for edge-case fixtures,
## never modified directly (CLAUDE.md).
_realResultsRoot = os.path.join(os.path.dirname(__file__), "..", "..", "GoogleTestResults")
## Edge-case XML fixtures directory (read-only).
_edgeCasesDir = os.path.join(os.path.dirname(__file__), "..", "fixtures", "edge_cases")


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


def runAppInBackground(app):
    """!
    @brief Start one Flask app in a daemon thread on a free port and wait for it.
    @param app A Flask app instance already wired to its results snapshot.
    @return Base URL (http://127.0.0.1:<port>) of the running server.
    """
    port = findFreePort()
    serverThread = threading.Thread(
        target=lambda: app.run(host="127.0.0.1", port=port, use_reloader=False),
        daemon=True,
    )
    serverThread.start()

    baseUrl = f"http://127.0.0.1:{port}"
    waitForServerReady(baseUrl)
    return baseUrl


@pytest.fixture(scope="session")
def liveServerUrl():
    """!
    @brief Run the real Flask app in a background thread for the test session.
    @return Base URL (http://127.0.0.1:<port>) of the running server.
    """
    return runAppInBackground(createApp())


@pytest.fixture
def corruptedXmlServerUrl(tmp_path):
    """!
    @brief Run a Flask app over a copy of the real dataset with one malformed
           XML injected into build 10 (FR-035: TC-FR-035-01/02).
    @param tmp_path pytest's per-test temporary directory.
    @return Base URL of a freshly started, per-test server.
    """
    copiedRoot = tmp_path / "GoogleTestResults"
    shutil.copytree(_realResultsRoot, copiedRoot)
    shutil.copy(
        os.path.join(_edgeCasesDir, "malformed.xml"),
        copiedRoot / "10" / "gtest_malformed_injected.xml",
    )
    return runAppInBackground(createApp(str(copiedRoot)))


@pytest.fixture
def statusPriorityServerUrl(tmp_path):
    """!
    @brief Run a Flask app over a synthetic build 99 exercising every single-
           evidence status marker (FR-006: TC-FR-006-05/06/13/14/15), reusing
           tests/fixtures/edge_cases/status_priority_conflict.xml which the
           unit-level status_resolver tests already rely on.
    @param tmp_path pytest's per-test temporary directory.
    @return Base URL of a freshly started, per-test server.
    """
    buildDir = tmp_path / "GoogleTestResults" / "99"
    buildDir.mkdir(parents=True)
    shutil.copy(
        os.path.join(_edgeCasesDir, "status_priority_conflict.xml"),
        buildDir / "gtest_status_priority.xml",
    )
    return runAppInBackground(createApp(str(tmp_path / "GoogleTestResults")))
