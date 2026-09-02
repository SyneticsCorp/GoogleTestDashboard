"""!
@file test_pagination.py
@brief Unit tests for FR-031 page-size-bounded slicing (src/gtestdash/query/pagination.py).
"""
from gtestdash.query.pagination import paginate


def test_paginate_defaultPageSize_isFifty():
    """!
    @brief Omitting pageSize defaults to 50 (FR-031).
    """
    records = list(range(120))

    result = paginate(records, page=1)

    assert result["pageSize"] == 50
    assert len(result["records"]) == 50


def test_paginate_onlyTwentyFiveFiftyOrOneHundredAreHonored():
    """!
    @brief An out-of-menu pageSize falls back to the 50 default (FR-031).
    """
    records = list(range(200))

    result = paginate(records, page=1, pageSize=13)

    assert result["pageSize"] == 50


def test_paginate_twentyFiveAndOneHundredAreBothHonored():
    """!
    @brief 25 and 100 are accepted page sizes, not just the 50 default (FR-031).
    """
    records = list(range(200))

    assert paginate(records, page=1, pageSize=25)["pageSize"] == 25
    assert paginate(records, page=1, pageSize=100)["pageSize"] == 100


def test_paginate_twelveHundredRecordsDefaultSize_hasTwentyFourPages():
    """!
    @brief FR-031 acceptance: 1,200 results at the default page size paginate into 24 pages.
    """
    records = list(range(1200))

    result = paginate(records, page=1)

    assert result["totalPages"] == 24
    assert result["totalMatches"] == 1200


def test_paginate_lastPage_hasCorrectDisplayRange():
    """!
    @brief The last of 24 pages displays records 1151-1200 (FR-031).
    """
    records = list(range(1200))

    result = paginate(records, page=24)

    assert result["displayRange"] == "1151-1200"
    assert len(result["records"]) == 50


def test_paginate_firstPage_displayRangeStartsAtOne():
    """!
    @brief The first page's display range starts at 1, not 0 (FR-031).
    """
    records = list(range(1200))

    result = paginate(records, page=1)

    assert result["displayRange"] == "1-50"


def test_paginate_pageBeyondLastPage_clampsToLastPage():
    """!
    @brief A page number beyond totalPages is clamped rather than returning an empty slice.
    """
    records = list(range(120))

    result = paginate(records, page=999, pageSize=50)

    assert result["page"] == 3
    assert result["records"] == records[100:120]


def test_paginate_emptyRecords_yieldsZeroPagesAndEmptySlice():
    """!
    @brief An empty result set yields totalPages 0 and an empty page, not an error (FR-036).
    """
    result = paginate([], page=1)

    assert result["totalPages"] == 0
    assert result["totalMatches"] == 0
    assert result["records"] == []
    assert result["displayRange"] == "0-0"


def test_paginate_pageLessThanOne_clampsToFirstPage():
    """!
    @brief A page number below 1 is clamped up to page 1.
    """
    records = list(range(120))

    result = paginate(records, page=0, pageSize=50)

    assert result["page"] == 1
    assert result["records"] == records[0:50]
