"""!
@file query_state.py
@brief FR-033: round-trip a list page's search/filter/sort/page state through a
       returnUrl query parameter carried by its test-detail links.

Each list route (build-detail, module-detail, search) builds its own current
URL with buildCurrentListUrl() and stamps it onto every row's test-detail link
via appendReturnUrlParam(); the test-detail route reads it back out of
request.args and renders it as the "목록으로 돌아가기" link, so navigating
away to a test and back restores the exact same query/filter/sort/page state.
"""
from urllib.parse import quote, urlencode


def buildCurrentListUrl(path, args):
    """!
    @brief Build the current list page's full URL (path + querystring) to round-trip (FR-033).
    @param path Request path, e.g. request.path.
    @param args Mapping of the current request's query args (e.g. request.args).
    @return "{path}?{querystring}" when args is non-empty, else path alone.
    """
    queryString = urlencode(dict(args))
    if not queryString:
        return path
    return f"{path}?{queryString}"


def appendReturnUrlParam(testUrl, currentListUrl):
    """!
    @brief Stamp a returnUrl query parameter carrying the current list page's URL (FR-033).
    @param testUrl A test-detail link (see route_helpers.buildTestDetailUrl()).
    @param currentListUrl The list page's own URL, from buildCurrentListUrl().
    @return testUrl with "returnUrl={percent-encoded currentListUrl}" appended,
            joined with "&" when testUrl already carries a querystring.
    """
    separator = "&" if "?" in testUrl else "?"
    return f"{testUrl}{separator}returnUrl={quote(currentListUrl, safe='')}"
