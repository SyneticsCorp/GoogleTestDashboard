"""!
@file test_final_acceptance.py
@brief Phase 7 completion gate: closes the one Requirements.md §8-7 gap found
       while auditing existing coverage against §7/§8 -- an entirely empty
       results root (zero build folders, "결과 없음") had never been
       exercised at the route level. Every other §7/§8 item already has
       explicit coverage elsewhere (see docs/acceptance-traceability.md); this
       file adds only what was missing, per the tdd-flow audit scope.
"""
import os

import pytest

from gtestdash.web.app import createApp

## Real, read-only dataset root; never modified by tests (CLAUDE.md).
_realResultsRoot = os.path.join(os.path.dirname(__file__), "..", "..", "GoogleTestResults")


@pytest.fixture
def emptyRootApp(tmp_path):
    """!
    @brief A Flask app wired to a results root that exists but has zero build
           folders -- the "결과 없음" condition distinct from a zero-failure
           build or a filter/search matching nothing within real data.
    @param tmp_path pytest tmp_path fixture; an empty directory by construction.
    @return The created Flask app (not yet queried).
    """
    return createApp(str(tmp_path))


def test_dashboardRoute_emptyResultsRoot_showsGuidanceAndNoException(emptyRootApp):
    """!
    @brief §8-7 acceptance: a results root with zero build folders does not
           crash the app -- GET / returns 200 and shows cause + next-action
           guidance instead of an empty dashboard (FR-001, FR-036).
    """
    response = emptyRootApp.test_client().get("/")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "표시할 빌드 결과가 없습니다" in body
    assert "GoogleTestResults 경로를 확인하세요" in body


def test_searchRoute_emptyResultsRoot_showsGuidanceAndNoException(emptyRootApp):
    """!
    @brief §8-7 acceptance: searching against a snapshot with zero records
           (not merely zero matches within real data) still renders guidance
           rather than raising (FR-036).
    """
    response = emptyRootApp.test_client().get("/search")

    assert response.status_code == 200
    assert "조건에 맞는 테스트가 없습니다" in response.get_data(as_text=True)


def test_dashboardRoute_realDataset_isUnaffectedByEmptyRootHandling():
    """!
    @brief Guardrail: the empty-root branch added above must not change
           behavior against the real dataset -- build 10 still leads with
           1,200/1,176/24/2.0% (§7).
    """
    app = createApp(_realResultsRoot)

    response = app.test_client().get("/")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "최신 빌드 10" in body
    assert "표시할 빌드 결과가 없습니다" not in body
