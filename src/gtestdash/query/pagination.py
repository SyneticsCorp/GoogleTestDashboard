"""!
@file pagination.py
@brief Page-size-bounded slicing with display-range metadata (FR-031).

Kept independent of search/filter/sort so any already-ordered record list can
be paginated the same way, whether it came from one build, one module or a
free-text search.
"""

## The only page sizes FR-031 allows; 50 is the default.
allowedPageSizes = (25, 50, 100)
## Default page size when none (or an invalid one) is requested (FR-031).
defaultPageSize = 50


def _normalizePageSize(pageSize):
    """!
    @brief Coerce a requested page size to one of FR-031's allowed sizes.
    @param pageSize Requested page size, or None for the default.
    @return One of allowedPageSizes; defaultPageSize when pageSize is not one of them.
    """
    if pageSize in allowedPageSizes:
        return pageSize
    return defaultPageSize


def _computeTotalPages(totalMatches, pageSize):
    """!
    @brief Ceiling-divide totalMatches by pageSize to get the page count.
    @param totalMatches Total number of records being paginated.
    @param pageSize Records shown per page (already normalized).
    @return Total pages needed; 0 when totalMatches is 0 (FR-036).
    """
    if totalMatches == 0:
        return 0
    return -(-totalMatches // pageSize)


def _normalizePage(page, totalPages):
    """!
    @brief Clamp a requested page number into [1, totalPages].
    @param page Requested 1-based page number.
    @param totalPages Total pages available for the current pageSize.
    @return 1 when totalPages is 0, else page clamped to [1, totalPages].
    """
    if totalPages <= 0:
        return 1
    return max(1, min(page, totalPages))


def _describeRange(startIndex, endIndex, hasRecords):
    """!
    @brief Build the FR-031 "current display range" string, e.g. "1-50".
    @param startIndex 0-based index of the page's first record.
    @param endIndex 0-based exclusive end index of the page's slice.
    @param hasRecords Whether the page actually contains any records.
    @return "{start+1}-{end}" when hasRecords, else "0-0" (FR-036 empty case).
    """
    if not hasRecords:
        return "0-0"
    return f"{startIndex + 1}-{endIndex}"


def paginate(records, page=1, pageSize=50):
    """!
    @brief Slice records into one FR-031 page, with display-range metadata.
    @param records Already searched/filtered/sorted list to paginate.
    @param page Requested 1-based page number; out-of-range values are clamped.
    @param pageSize Requested page size; only 25/50/100 are honored (FR-031).
    @return Dict with "records" (this page's slice), "page", "pageSize",
            "totalMatches", "totalPages" and "displayRange".
    """
    normalizedSize = _normalizePageSize(pageSize)
    totalMatches = len(records)
    totalPages = _computeTotalPages(totalMatches, normalizedSize)
    normalizedPage = _normalizePage(page, totalPages)

    startIndex = (normalizedPage - 1) * normalizedSize
    endIndex = min(startIndex + normalizedSize, totalMatches)
    pageRecords = records[startIndex:endIndex]

    return {
        "records": pageRecords,
        "page": normalizedPage,
        "pageSize": normalizedSize,
        "totalMatches": totalMatches,
        "totalPages": totalPages,
        "displayRange": _describeRange(startIndex, endIndex, bool(pageRecords)),
    }
