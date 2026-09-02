"""!
@file module_distribution.py
@brief Module-level failure distribution for the main dashboard chart (FR-014, FR-015).
"""
from urllib.parse import quote

from gtestdash.aggregation.build_summary import computeCounts, computeFailureRate
from gtestdash.aggregation.grouping import groupRecordsByBuild
from gtestdash.aggregation.latest_build import resolveLatestBuild


def buildModuleDrilldownUrl(buildId, module):
    """!
    @brief Build the module-detail URL a chart bar click should navigate to (FR-015).
    @param buildId Build id the drilldown targets.
    @param module Module name the drilldown targets.
    @return Path per Requirements.md §5 (`/builds/{build_id}/modules/{module}`)
            with the failed-only filter pre-enabled, per FR-015's requirement
            that the destination page defaults to showing only failed tests.
    """
    return f"/builds/{buildId}/modules/{quote(module, safe='')}?failedOnly=true"


def _resolveLatestBuildId(records):
    """!
    @brief Determine the latest build id present among records (FR-009).
    @param records Full or already-scoped ResultRecord list.
    @return Latest build id string, or None when records is empty.
    """
    builds = [
        {"buildId": buildId, "buildTimestamp": buildRecords[0].build_timestamp}
        for buildId, buildRecords in groupRecordsByBuild(records).items()
    ]
    latest = resolveLatestBuild(builds)
    return latest["buildId"] if latest else None


def _normalizeBuildId(records, scope):
    """!
    @brief Match a caller-supplied scope value against the build ids present.
    @param records Full ResultRecord list, used to discover valid build ids.
    @param scope Requested scope: a build id, as str or int.
    @return The matching build_id string as it appears on the records, or the
            stringified scope unchanged when nothing matches (yields no records).
    """
    scopeStr = str(scope)
    presentIds = {record.build_id for record in records}
    if scopeStr in presentIds:
        return scopeStr
    for buildId in presentIds:
        if buildId.isdigit() and scopeStr.isdigit() and int(buildId) == int(scopeStr):
            return buildId
    return scopeStr


def _resolveScopeBuildId(records, scope):
    """!
    @brief Resolve a scope value ("latest"/"cumulative"/build id) to a build id or None.
    @param records Full ResultRecord list.
    @param scope Scope selector; see computeModuleDistribution().
    @return None for "cumulative" (no single build applies); otherwise the
            resolved build id string.
    """
    if scope == "cumulative":
        return None
    if scope == "latest":
        return _resolveLatestBuildId(records)
    return _normalizeBuildId(records, scope)


def _groupByModule(records):
    """!
    @brief Split records into per-module lists, insertion order preserved.
    @param records ResultRecord list already filtered to the desired scope.
    @return Dict mapping module name -> list of ResultRecord.
    """
    grouped = {}
    for record in records:
        grouped.setdefault(record.module, []).append(record)
    return grouped


def _summarizeModule(module, moduleRecords, linkBuildId):
    """!
    @brief Fold one module's scoped records into a chart-ready distribution entry (FR-014).
    @param module Module name.
    @param moduleRecords ResultRecord list for this module, within the chosen scope.
    @param linkBuildId Build id the drilldown URL should target (FR-015).
    @return Dict with module, total, failed, failureRate and moduleUrl.
    """
    counts = computeCounts(moduleRecords)
    return {
        "module": module,
        "total": counts["total"],
        "failed": counts["failed"],
        "failureRate": computeFailureRate(counts),
        "moduleUrl": buildModuleDrilldownUrl(linkBuildId, module),
    }


def computeModuleDistribution(records, scope="latest"):
    """!
    @brief Compute per-module failure counts for the main dashboard chart (FR-014).
    @param records Full list of ResultRecord across every build.
    @param scope "latest" (default: highest-numbered build only), "cumulative"
           (every build summed), or a specific build id (str or int).
    @return List of per-module dicts (module, total, failed, failureRate,
            moduleUrl), sorted by failed count descending (FR-014). Drilldown
            URLs target the resolved scope build, falling back to the latest
            build for the "cumulative" scope (FR-015).
    """
    scopeBuildId = _resolveScopeBuildId(records, scope)
    filteredRecords = records if scopeBuildId is None else [
        record for record in records if record.build_id == scopeBuildId
    ]
    linkBuildId = scopeBuildId or _resolveLatestBuildId(records)

    moduleGroups = _groupByModule(filteredRecords)
    distribution = [_summarizeModule(module, moduleRecords, linkBuildId) for module, moduleRecords in moduleGroups.items()]
    distribution.sort(key=lambda entry: entry["failed"], reverse=True)
    return distribution
