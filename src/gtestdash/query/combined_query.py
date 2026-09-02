"""!
@file combined_query.py
@brief Single entry point combining search, filters, sort and pagination (FR-029).

Shared by the build-detail, module-detail and search-results routes: each
passes the full record list plus whichever dimensions its URL already fixes
(e.g. build-detail fixes buildId), and gets back one page of results together
with the metadata every list page needs to render (FR-025~031).
"""
from gtestdash.query.class_filters import applyClassFilters, availableFilterValues
from gtestdash.query.pagination import paginate
from gtestdash.query.sorting import sortRecords
from gtestdash.query.text_search import searchRecords


def _scopeToFailedOnly(records, failedOnly):
    """!
    @brief Narrow to FAILED-status records when the failed-only toggle is on (FR-025).
    @param records Already searched+classified record list.
    @param failedOnly Whether the failed-only toggle is active.
    @return records unchanged when failedOnly is False, else only FAILED records.
    """
    if not failedOnly:
        return records
    return [record for record in records if record.status == "FAILED"]


def runCombinedQuery(
    records,
    queryText=None,
    failedOnly=False,
    status=None,
    buildId=None,
    module=None,
    functionOrSuite=None,
    sortKey=None,
    page=1,
    pageSize=50,
):
    """!
    @brief Apply search, classification filters, failed-only, sort and pagination together (FR-029).
    @param records ResultRecord list already scoped to the page's own context
           (e.g. the full snapshot; build/module scoping happens via buildId/module below).
    @param queryText FR-026 free-text search, or None/"" for no text filter.
    @param failedOnly When True, keeps only FAILED records (FR-025).
    @param status Exact status filter (FR-028), applied in addition to failedOnly.
    @param buildId Exact build_id filter (FR-028); build-detail/module-detail
           routes pass their URL's build id here to scope the search (FR-027).
    @param module Exact module filter (FR-028); module-detail passes its
           URL's module here (FR-027).
    @param functionOrSuite Exact function-or-suite filter (FR-021, FR-028).
    @param sortKey One of sorting.sortRecords()'s supported keys, or None.
    @param page 1-based page number (FR-031).
    @param pageSize One of 25/50/100 (FR-031); other values fall back to 50.
    @return Dict: "records" (this page's ResultRecord slice), "page",
            "pageSize", "totalMatches", "totalPages", "displayRange" (see
            pagination.paginate()) plus "filterOptions" (availableFilterValues()
            computed after the text search and every classification filter
            (buildId/module/status/functionOrSuite), so a page scoped to one
            build+module never leaks another build's or module's values
            (FR-028), but before failedOnly narrows further).
    """
    searched = searchRecords(records, queryText)
    classified = applyClassFilters(
        searched, status=status, buildId=buildId, module=module, functionOrSuite=functionOrSuite
    )
    filterOptions = availableFilterValues(classified)

    scoped = _scopeToFailedOnly(classified, failedOnly)
    ordered = sortRecords(scoped, sortKey=sortKey, failedOnly=failedOnly)

    pageResult = paginate(ordered, page=page, pageSize=pageSize)
    pageResult["filterOptions"] = filterOptions
    return pageResult
