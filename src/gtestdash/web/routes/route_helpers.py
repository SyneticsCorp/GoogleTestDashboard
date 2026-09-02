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
            percent-encoded "{classname}.{test_name}" pair (FR-022).
    """
    return f"/builds/{record.build_id}/tests/{quote(_testIdSlug(record), safe='')}"


def _testIdSlug(record):
    """!
    @brief Build the unencoded "{classname}.{test_name}" slug for one record.
    @param record ResultRecord to derive the slug from.
    @return The "{classname}.{test_name}" string, shared by buildTestDetailUrl()
            and findRecordByTestId() so the encode/decode stay in sync.
    """
    return f"{record.classname}.{record.test_name}"


def findRecordByTestId(records, buildId, testId):
    """!
    @brief Reverse-lookup the ResultRecord a test-detail test_id refers to (FR-022).

    Relies on classname+test_name being unique within one build's records, as
    buildTestDetailUrl() assumes when building the slug. Accepts testId either
    already percent-decoded (as Flask hands route parameters) or still encoded,
    so callers do not need to know which form they hold.
    @param records Full ResultRecord list across every build.
    @param buildId Build id the requested test_id must belong to.
    @param testId The "{classname}.{test_name}" slug, decoded or encoded.
    @return The matching ResultRecord, or None when no record matches.
    """
    for record in records:
        if record.build_id != buildId:
            continue
        slug = _testIdSlug(record)
        if testId in (slug, quote(slug, safe="")):
            return record
    return None
