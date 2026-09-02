"""!
@file route_helpers.py
@brief Route-building helpers shared across dashboard/builds/modules routes.

Centralized so the test-detail link shape (Requirements.md §5:
`/builds/{build_id}/tests/{test_id}`) is defined once instead of duplicated
in every route module that lists tests.
"""
from urllib.parse import quote


def buildTestDetailUrl(record):
    """!
    @brief Build the test-detail URL for one ResultRecord (Requirements.md §5 path shape).
    @param record ResultRecord to link to.
    @return Path `/builds/{build_id}/tests/{test_id}`, where test_id is the
            percent-encoded "{classname}.{test_name}" pair; the route itself
            is added in a later phase (FR-022), so this may 404 for now.
    """
    testId = quote(f"{record.classname}.{record.test_name}", safe="")
    return f"/builds/{record.build_id}/tests/{testId}"
