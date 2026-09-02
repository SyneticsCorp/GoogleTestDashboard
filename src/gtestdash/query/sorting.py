"""!
@file sorting.py
@brief Stable sorting for test-record lists (FR-030).

Built on Python's sorted(), which is guaranteed stable: records that compare
equal on the chosen key keep their original relative order, so a page that is
re-rendered under identical conditions never reshuffles (FR-030's acceptance
criterion).
"""

## Maps a user-facing sortKey to the ResultRecord attribute it sorts by.
_sortKeyFields = {
    "status": "status",
    "module": "module",
    "functionOrSuite": "function",
    "testName": "test_name",
    "duration": "duration_seconds",
}


def _defaultFailedOnlyKey(record):
    """!
    @brief FR-030's default stable sort key for the failed-only view.
    @param record ResultRecord to derive the key from.
    @return Tuple (module, function, test_name), the required default order.
    """
    return (record.module, record.function, record.test_name)


def sortRecords(records, sortKey=None, failedOnly=False):
    """!
    @brief Stable-sort records by one of FR-030's supported keys.
    @param records ResultRecord list to sort.
    @param sortKey One of "status", "module", "functionOrSuite", "testName",
           "duration", or None to skip explicit sorting.
    @param failedOnly When True and sortKey is None, applies FR-030's default
           failed-only ordering (module, then function/suite, then test name).
    @return New list, stably sorted; unchanged order when neither sortKey nor
            failedOnly applies.
    """
    if sortKey in _sortKeyFields:
        fieldName = _sortKeyFields[sortKey]
        return sorted(records, key=lambda record: getattr(record, fieldName))
    if failedOnly:
        return sorted(records, key=_defaultFailedOnlyKey)
    return list(records)
