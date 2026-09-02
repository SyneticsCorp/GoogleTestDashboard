"""!
@file route_helpers.py
@brief Route-building helpers shared across dashboard/builds/modules routes.

Centralized so the test-detail link shape (Requirements.md §5:
`/builds/{build_id}/tests/{test_id}`) is defined once instead of duplicated
in every route module that lists tests.
"""
from urllib.parse import quote, urlencode


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


def buildListPageUrl(basePath, currentArgs, **overrides):
    """!
    @brief Build a same-page URL merging currentArgs with overrides (FR-031 pagination links).

    Used to build "이전/다음 페이지" links (and similar same-page links) that
    keep every other active search/filter/sort query parameter untouched
    (a building block for FR-033's later state-preservation work).
    @param basePath Path to link to, e.g. request.path.
    @param currentArgs Mapping of the page's current query args (e.g. request.args).
    @param overrides Query keys to set/replace; a value of None removes the key.
    @return "{basePath}?{querystring}", or basePath alone when no params remain.
    """
    merged = dict(currentArgs)
    for key, value in overrides.items():
        if value is None:
            merged.pop(key, None)
        else:
            merged[key] = value
    if not merged:
        return basePath
    return f"{basePath}?{urlencode(merged, doseq=True)}"


def _parseIntArg(args, key, default):
    """!
    @brief Parse one query arg as an int, falling back to default when absent or invalid.
    @param args Mapping of query args (e.g. request.args, or a plain dict in tests).
    @param key Query parameter name to read.
    @param default Value to return when key is absent or not a valid int.
    @return The parsed int, or default.
    """
    rawValue = args.get(key)
    if rawValue is None:
        return default
    try:
        return int(rawValue)
    except (TypeError, ValueError):
        return default


def readListQueryArgs(args, includeBuildId=False, includeModule=False):
    """!
    @brief Parse the FR-025~031 query parameters shared by every list route.

    Centralizes the query-string shape all three list routes (build-detail,
    module-detail, search) read, so it is defined once instead of duplicated
    per route (CLAUDE.md's no-duplicate-code rule).
    @param args Mapping of query args (e.g. Flask's request.args).
    @param includeBuildId Whether to also read a "buildId" filter (search route).
    @param includeModule Whether to also read a "module" filter (build-detail/search).
    @return Dict of keyword arguments ready for runCombinedQuery() or one of
            the *DetailContext() builders: queryText, failedOnly, status,
            functionOrSuite, sortKey, page, pageSize, plus buildId/module
            when requested.
    """
    queryArgs = {
        "queryText": args.get("q") or None,
        "failedOnly": args.get("failedOnly") == "true",
        "status": args.get("status") or None,
        "functionOrSuite": args.get("functionOrSuite") or None,
        "sortKey": args.get("sort") or None,
        "page": _parseIntArg(args, "page", 1),
        "pageSize": _parseIntArg(args, "pageSize", 50),
    }
    if includeBuildId:
        queryArgs["buildId"] = args.get("buildId") or None
    if includeModule:
        queryArgs["module"] = args.get("module") or None
    return queryArgs


def attachPageNavLinks(context, path, args):
    """!
    @brief Add prevPageUrl/nextPageUrl to a list-page context, preserving other query state (FR-031).

    Shared by build-detail and module-detail (and reusable by search), so the
    prev/next link logic is defined once instead of duplicated per route.
    @param context Context dict already containing "page" and "totalPages"
           (as returned by query.combined_query.runCombinedQuery()); mutated in place.
    @param path The route's own path (request.path), to link back to.
    @param args Current request.args, so every other filter/sort param is preserved.
    """
    currentPage = context["page"]
    context["prevPageUrl"] = buildListPageUrl(path, args, page=currentPage - 1) if currentPage > 1 else None
    context["nextPageUrl"] = (
        buildListPageUrl(path, args, page=currentPage + 1) if currentPage < context["totalPages"] else None
    )
