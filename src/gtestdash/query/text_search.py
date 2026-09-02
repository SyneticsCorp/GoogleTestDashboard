"""!
@file text_search.py
@brief Case-insensitive substring search over FR-026's nine searchable fields.

Shared by the build-detail, module-detail and search-results routes so all
three list pages search the exact same fields the same way (FR-026, FR-029).
"""

## ResultRecord attribute names FR-026 requires text search to cover.
searchableFields = (
    "module",
    "function",
    "suite",
    "test_name",
    "classname",
    "test_file",
    "source_file",
    "failure_summary",
    "failure_detail",
)


def _recordMatchesQuery(record, lowerQuery):
    """!
    @brief Check whether one record's searchable fields contain lowerQuery.
    @param record ResultRecord to test.
    @param lowerQuery Already-lowercased search text.
    @return True when any of searchableFields contains lowerQuery, case-insensitively.
    """
    for fieldName in searchableFields:
        fieldValue = getattr(record, fieldName)
        if fieldValue and lowerQuery in fieldValue.lower():
            return True
    return False


def searchRecords(records, queryText):
    """!
    @brief Case-insensitive substring search over FR-026's nine text fields.
    @param records ResultRecord list to search.
    @param queryText Search text; falsy (None or "") returns records unchanged,
           which is what "전체 초기화" (FR-029) relies on.
    @return New list of records matching queryText in at least one searchable field.
    """
    if not queryText:
        return list(records)
    lowerQuery = queryText.lower()
    return [record for record in records if _recordMatchesQuery(record, lowerQuery)]
