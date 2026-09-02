"""!
@file class_filters.py
@brief Status/build/module/function-or-suite classification filters (FR-028).

availableFilterValues() only ever surfaces values that actually occur in the
current result set, so a filter dropdown never offers a module or suite the
data does not contain (FR-028's acceptance criterion).
"""
from gtestdash.aggregation.grouping import numericBuildIdSortKey


def availableFilterValues(records):
    """!
    @brief Collect filter option values that actually occur in records (FR-028).
    @param records ResultRecord list currently in scope (e.g. after text search).
    @return Dict with sorted unique lists for "status", "buildId" (numeric
            order), "module" and "functionOrSuite" (function values union
            suite values, per FR-021's single function-or-suite filter).
    """
    return {
        "status": sorted({record.status for record in records}),
        "buildId": sorted({record.build_id for record in records}, key=numericBuildIdSortKey),
        "module": sorted({record.module for record in records}),
        "functionOrSuite": sorted({record.function for record in records} | {record.suite for record in records}),
    }


def _keepMatching(records, fieldName, expectedValue):
    """!
    @brief Keep only records whose fieldName attribute equals expectedValue.
    @param records ResultRecord list to filter.
    @param fieldName ResultRecord attribute name to compare.
    @param expectedValue Value records must match; falsy means "no filter".
    @return records unchanged when expectedValue is falsy, else the filtered list.
    """
    if not expectedValue:
        return records
    return [record for record in records if getattr(record, fieldName) == expectedValue]


def applyClassFilters(records, status=None, buildId=None, module=None, functionOrSuite=None):
    """!
    @brief Apply status/build/module/function-or-suite filters in combination (FR-028).
    @param records ResultRecord list to filter.
    @param status Exact status to keep (e.g. "FAILED"), or None for no filter.
    @param buildId Exact build_id to keep, or None for no filter.
    @param module Exact module to keep, or None for no filter.
    @param functionOrSuite Exact function or suite value to keep (matches
           either field, per FR-021), or None for no filter.
    @return Filtered ResultRecord list with every supplied filter applied (AND).
    """
    filtered = _keepMatching(records, "status", status)
    filtered = _keepMatching(filtered, "build_id", buildId)
    filtered = _keepMatching(filtered, "module", module)
    if functionOrSuite:
        filtered = [
            record
            for record in filtered
            if record.function == functionOrSuite or record.suite == functionOrSuite
        ]
    return filtered
