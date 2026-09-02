"""!
@file grouping.py
@brief Shared record-by-build grouping and numeric build-id ordering.

Several aggregation modules (build_history, latest_build, trend,
module_distribution) all need to split records by build_id and order builds
numerically ("09" before "10", per FR-002's ordering rule extended to
aggregation). Centralized here so that ordering logic has one definition.
"""


def groupRecordsByBuild(records):
    """!
    @brief Split a flat record list into per-build_id lists, insertion order preserved.
    @param records List of ResultRecord.
    @return Dict mapping build_id -> list of ResultRecord belonging to that build.
    """
    grouped = {}
    for record in records:
        grouped.setdefault(record.build_id, []).append(record)
    return grouped


def numericBuildIdSortKey(buildId):
    """!
    @brief Sort key ordering numeric build ids by value, non-numeric ids after.
    @param buildId Build id string (e.g. "09", "10", "release-a").
    @return Tuple placing numeric ids before non-numeric ones, numeric-first.
    """
    if buildId.isdigit():
        return (0, int(buildId), buildId)
    return (1, 0, buildId)
