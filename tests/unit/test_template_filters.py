"""!
@file test_template_filters.py
@brief Unit tests for dashboard display-formatting helpers (src/gtestdash/web/template_filters.py).
"""
from gtestdash.web.template_filters import formatPercent, formatPercentDiff


def test_formatPercent_rendersOneDecimalPlaceWithPercentSign():
    """!
    @brief FR-010: failure rate displays with exactly one decimal place.
    """
    assert formatPercent(2.0) == "2.0%"


def test_formatPercent_passesThroughNotApplicable():
    """!
    @brief FR-007: the "N/A" sentinel is shown verbatim, never "0.0%".
    """
    assert formatPercent("N/A") == "N/A"


def test_formatPercentDiff_showsPlusSignForIncrease():
    """!
    @brief FR-011: an increase is shown with an explicit "+" sign.
    """
    assert formatPercentDiff(2.0) == "+2.0%p"


def test_formatPercentDiff_showsMinusSignForDecrease():
    """!
    @brief FR-011 acceptance: build 10 vs 09 renders as "-2.0%p".
    """
    assert formatPercentDiff(-2.0) == "-2.0%p"


def test_formatPercentDiff_rendersNotApplicable_whenNoDiffAvailable():
    """!
    @brief No previous build (or a non-numeric rate) has nothing to show.
    """
    assert formatPercentDiff(None) == "N/A"
