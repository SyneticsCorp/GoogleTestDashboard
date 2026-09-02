"""!
@file models.py
@brief Pure data structures for parsed GoogleTest results (Requirements.md §4.3).

These dataclasses carry no behavior; they are exercised indirectly through the
tests for the functions that build and consume them (record_builder,
xml_parser, validation, repository).
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ResultRecord:
    """!
    @brief One normalized `<testcase>` record (Requirements.md §4.3).

    Field names intentionally use snake_case to mirror Requirements.md §4.3's
    original field names verbatim, as documented as the sole exception to this
    project's camelCase naming convention (CLAUDE.md).
    """

    ## Jenkins build identifier (`jenkins_build_number` or folder name).
    build_id: str
    ## Build timestamp (`testsuites@timestamp` or `testsuite@timestamp`).
    build_timestamp: Optional[str]
    ## Module name (`property[name=module]`, with fallbacks).
    module: str
    ## Test suite / fixture name (`testsuite@name`).
    suite: str
    ## Function under test (`property[name=tested_function]`, with fallback).
    function: str
    ## Test case name (`testcase@name`).
    test_name: str
    ## GoogleTest class name (`testcase@classname`).
    classname: str
    ## Normalized status: PASSED, FAILED, ERROR, SKIPPED, DISABLED.
    status: str
    ## Duration in seconds (`testcase@time`).
    duration_seconds: float
    ## Test execution timestamp (`testcase@timestamp`).
    timestamp: Optional[str]
    ## Test source file (`testcase@file`).
    test_file: Optional[str]
    ## Test source line number (`testcase@line`).
    line: Optional[int]
    ## Failure type (`failure@type`), when present.
    failure_type: Optional[str]
    ## Failure summary (`failure@message`), when present.
    failure_summary: Optional[str]
    ## Full failure body text (`<failure>` element text), when present.
    failure_detail: Optional[str]
    ## Source file under test (`property[name=source_file]`).
    source_file: Optional[str]
    ## Synthetic-data marker (`property[name=synthetic_data]`).
    synthetic_data: Optional[str]


@dataclass
class ParseWarning:
    """!
    @brief A non-fatal parsing/aggregation warning (FR-008, FR-035).

    Carries the offending XML path plus enough context (declared vs. computed
    values, or a parse error message) to render a diagnostic to the user.
    """

    ## Absolute or relative path to the XML file the warning concerns.
    xmlPath: str
    ## Short machine-friendly category, e.g. "count_mismatch" or "parse_error".
    kind: str
    ## Human-readable explanation of the warning.
    message: str
    ## Declared counts dict, when this warning is a declared-vs-computed mismatch.
    declaredCounts: Optional[dict] = None
    ## Computed counts dict, when this warning is a declared-vs-computed mismatch.
    computedCounts: Optional[dict] = None


@dataclass
class BuildInfo:
    """!
    @brief Identity of one discovered build folder (FR-002).
    """

    ## Folder name as found on disk (e.g. "01", "10").
    folderName: str
    ## Absolute path to the build folder.
    folderPath: str
