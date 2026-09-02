"""!
@file test_snapshot_acceptance.py
@brief Phase 1 completion gate: Requirements.md §7 acceptance criteria against
       the real, read-only GoogleTestResults dataset.
"""
import os

from gtestdash.aggregation.build_summary import computeCounts, computeFailureRate
from gtestdash.parsing.discovery import findBuildFolders, findXmlFiles
from gtestdash.repository import buildSnapshot

## Real dataset root; never modified by tests (CLAUDE.md: read-only fixture data).
_resultsRoot = os.path.join(os.path.dirname(__file__), "..", "..", "GoogleTestResults")

## Expected per-build failure rate percentages, build 01 through 10, per §7.
_expectedFailureRatesByBuild = [8, 4, 9, 6, 3, 7, 5, 10, 4, 2]


def test_discovery_findsTenBuildsAndOneHundredXmlFiles():
    """!
    @brief §7: 10 builds, 100 XML files total (FR-002, FR-003).
    """
    builds = findBuildFolders(_resultsRoot)

    assert [build.folderName for build in builds] == [f"{n:02d}" for n in range(1, 11)]

    totalXmlFiles = sum(len(findXmlFiles(build.folderPath)) for build in builds)
    assert totalXmlFiles == 100


def test_buildSnapshot_hasNoWarningsAndTwelveThousandRecords():
    """!
    @brief §7/§8: all 100 XML files parse cleanly into 12,000 records, with no
           corruption or count-mismatch warnings against this known-good dataset.
    """
    snapshot = buildSnapshot(_resultsRoot)

    assert snapshot.excludedFiles == []
    assert snapshot.warnings == []
    assert len(snapshot.records) == 12000


def test_buildSnapshot_perBuildFailureRatesMatchExpectedSequence():
    """!
    @brief §7: builds 01..10 have failure rates 8,4,9,6,3,7,5,10,4,2 percent (FR-007).
    """
    snapshot = buildSnapshot(_resultsRoot)

    failureRatesByBuild = []
    for buildNumber in range(1, 11):
        buildId = f"{buildNumber:02d}"
        recordsForBuild = [record for record in snapshot.records if record.build_id == buildId]
        counts = computeCounts(recordsForBuild)
        failureRatesByBuild.append(computeFailureRate(counts))

    assert failureRatesByBuild == _expectedFailureRatesByBuild


def test_buildSnapshot_build10HasExactCountsFromSpec():
    """!
    @brief §7: build 10 has 1,200 total / 1,176 passed / 24 failed / 2.0% failure rate.
    """
    snapshot = buildSnapshot(_resultsRoot)
    build10Records = [record for record in snapshot.records if record.build_id == "10"]

    counts = computeCounts(build10Records)

    assert counts["total"] == 1200
    assert counts["passed"] == 1176
    assert counts["failed"] == 24
    assert computeFailureRate(counts) == 2.0
