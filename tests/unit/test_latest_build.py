"""!
@file test_latest_build.py
@brief Unit tests for latest-build resolution (src/gtestdash/aggregation/latest_build.py, FR-009).
"""
from gtestdash.aggregation.latest_build import resolveLatestBuild


def test_resolveLatestBuild_picksHighestNumericBuildId():
    """!
    @brief Among numeric build ids, the maximum wins (FR-009 tier 1/2).
    """
    builds = [
        {"buildId": "01", "buildTimestamp": "2026-01-01T00:00:00Z"},
        {"buildId": "10", "buildTimestamp": "2026-01-02T00:00:00Z"},
        {"buildId": "09", "buildTimestamp": "2026-01-03T00:00:00Z"},
    ]

    latest = resolveLatestBuild(builds)

    assert latest["buildId"] == "10"


def test_resolveLatestBuild_fallsBackToTimestamp_whenNoBuildIdIsNumeric():
    """!
    @brief With no numeric build id available, the latest timestamp wins (FR-009 tier 3).
    """
    builds = [
        {"buildId": "release-a", "buildTimestamp": "2026-01-01T00:00:00Z"},
        {"buildId": "release-b", "buildTimestamp": "2026-03-01T00:00:00Z"},
    ]

    latest = resolveLatestBuild(builds)

    assert latest["buildId"] == "release-b"


def test_resolveLatestBuild_returnsNone_forEmptyBuildList():
    """!
    @brief No builds at all: no latest build, not an exception (FR-036 spirit).
    """
    assert resolveLatestBuild([]) is None
