"""!
@file test_build_summary.py
@brief Unit tests for FR-007 count/failure-rate recomputation
       (src/gtestdash/aggregation/build_summary.py).
"""
from gtestdash.aggregation.build_summary import computeCounts, computeFailureRate
from gtestdash.parsing.models import ResultRecord


def _makeRecord(status):
    """!
    @brief Build a minimal ResultRecord with only the fields the counters read.
    @param status Normalized status string to assign the record.
    @return A ResultRecord with placeholder values for every other field.
    """
    return ResultRecord(
        build_id="01",
        build_timestamp=None,
        module="Mod",
        suite="Mod.Suite",
        function="Func",
        test_name="Func_Case",
        classname="Mod.Suite",
        status=status,
        duration_seconds=0.1,
        timestamp=None,
        test_file=None,
        line=None,
        failure_type=None,
        failure_summary=None,
        failure_detail=None,
        source_file=None,
        synthetic_data=None,
    )


def test_computeCounts_tallysEachStatusFromRecords_notXmlDeclaredValues():
    """!
    @brief Counts are recomputed from records, not trusted from XML (FR-007).
    """
    records = [
        _makeRecord("PASSED"),
        _makeRecord("PASSED"),
        _makeRecord("FAILED"),
        _makeRecord("ERROR"),
        _makeRecord("SKIPPED"),
        _makeRecord("DISABLED"),
    ]

    counts = computeCounts(records)

    assert counts == {"total": 6, "passed": 2, "failed": 1, "error": 1, "skipped": 1, "disabled": 1}


def test_computeCounts_returnsAllZeros_forEmptyRecordList():
    """!
    @brief An empty record set yields all-zero counts, not an error (FR-036).
    """
    assert computeCounts([]) == {"total": 0, "passed": 0, "failed": 0, "error": 0, "skipped": 0, "disabled": 0}


def test_computeFailureRate_isFailedOverTotalTimesOneHundred():
    """!
    @brief Failure rate = failed / total * 100, per FR-007's formula.
    """
    counts = {"total": 1200, "passed": 1176, "failed": 24, "error": 0, "skipped": 0, "disabled": 0}

    assert computeFailureRate(counts) == 2.0


def test_computeFailureRate_returnsNotApplicableString_whenTotalIsZero():
    """!
    @brief Zero total tests: failure rate is the string "N/A", not the number 0 (FR-007).
    """
    counts = {"total": 0, "passed": 0, "failed": 0, "error": 0, "skipped": 0, "disabled": 0}

    result = computeFailureRate(counts)

    assert result == "N/A"
    assert result != 0
