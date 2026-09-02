"""!
@file build_summary.py
@brief Recompute counts and failure rate from normalized records (FR-007).

Aggregate values are always derived from the parsed ResultRecord list, never
trusted from the XML's own declared totals (see validation.py for the
declared-vs-computed cross-check).
"""

## Normalized statuses tallied by computeCounts(), lowercased for count keys.
_countedStatuses = ["passed", "failed", "error", "skipped", "disabled"]


def computeCounts(records):
    """!
    @brief Recompute total/passed/failed/error/skipped/disabled from records (FR-007).
    @param records List of ResultRecord.
    @return Dict with keys "total" plus one per _countedStatuses, all ints;
            an empty record list yields all zeros (FR-036).
    """
    counts = {"total": len(records)}
    counts.update({statusKey: 0 for statusKey in _countedStatuses})
    for record in records:
        statusKey = record.status.lower()
        if statusKey in counts:
            counts[statusKey] += 1
    return counts


def computeFailureRate(counts):
    """!
    @brief Compute failure rate = failed / total * 100, rounded to 1 decimal (FR-007).
    @param counts Dict as returned by computeCounts().
    @return Float percentage rounded to 1 decimal place, or the string "N/A"
            when total is 0 (never the number 0, per FR-007).
    """
    if counts["total"] == 0:
        return "N/A"
    return round(counts["failed"] / counts["total"] * 100, 1)
