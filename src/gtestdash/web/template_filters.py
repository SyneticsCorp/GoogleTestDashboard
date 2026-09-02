"""!
@file template_filters.py
@brief Jinja display-formatting helpers for percentages (FR-007, FR-010, FR-011).

Kept separate from the aggregation layer so aggregation functions can keep
returning raw values (float or the "N/A" sentinel) for JSON/chart use, while
templates render a consistently formatted string via these filters.
"""


def formatPercent(rateValue):
    """!
    @brief Format a failure rate for display (FR-010).
    @param rateValue Float percentage or the string "N/A".
    @return "N/A" unchanged, otherwise the value with one decimal place and a
            trailing "%" (e.g. 2.0 -> "2.0%").
    """
    if isinstance(rateValue, str):
        return rateValue
    return f"{rateValue:.1f}%"


def formatPercentDiff(diffValue):
    """!
    @brief Format a build-over-build failure-rate delta for display (FR-011).
    @param diffValue Signed float percentage-point delta, or None when there
           is no previous build (or either rate is "N/A") to compare against.
    @return "N/A" when diffValue is None, otherwise a signed value with one
            decimal place and a trailing "%p" (e.g. -2.0 -> "-2.0%p").
    """
    if diffValue is None:
        return "N/A"
    return f"{diffValue:+.1f}%p"
