"""!
@file test_query_state.py
@brief Unit tests for FR-033 return-url round-tripping (src/gtestdash/query/query_state.py).
"""
from gtestdash.query.query_state import appendReturnUrlParam, buildCurrentListUrl


def test_buildCurrentListUrl_withQueryArgs_includesThemInOrder():
    """!
    @brief FR-033: the list page's own querystring is preserved verbatim in the built URL.
    """
    url = buildCurrentListUrl("/search", {"status": "FAILED", "page": "2"})

    assert url == "/search?status=FAILED&page=2"


def test_buildCurrentListUrl_noArgs_returnsBarePath():
    """!
    @brief FR-033: a list page with no active query state returns just the path.
    """
    url = buildCurrentListUrl("/builds/10", {})

    assert url == "/builds/10"


def test_appendReturnUrlParam_encodesReturnUrlAsQueryValue():
    """!
    @brief FR-033: returnUrl is percent-encoded so its own "?"/"&" survive as one query value.
    """
    testUrl = "/builds/10/tests/Foo.Bar"

    result = appendReturnUrlParam(testUrl, "/search?status=FAILED&page=2")

    assert result == "/builds/10/tests/Foo.Bar?returnUrl=%2Fsearch%3Fstatus%3DFAILED%26page%3D2"


def test_appendReturnUrlParam_urlAlreadyHasQuery_usesAmpersandSeparator():
    """!
    @brief FR-033: appending returnUrl to a testUrl that already carries a query
           string uses "&", not a second "?".
    """
    result = appendReturnUrlParam("/builds/10/tests/Foo.Bar?x=1", "/search")

    assert result == "/builds/10/tests/Foo.Bar?x=1&returnUrl=%2Fsearch"
