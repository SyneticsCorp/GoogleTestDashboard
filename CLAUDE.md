# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository status

This repository currently contains **no application code** — it is the specification and sample
dataset for a web app that has not been built yet. There is no build system, package manifest, test
runner, or git repository present. Before writing code, check whether an implementation has since
been added (e.g. a `src/`, `app/`, or similar directory, plus a `requirements.txt`/`pyproject.toml`);
if so, treat that as authoritative over this file and update this file to document its actual
commands and architecture.

## What this repo is for

`Requirements.md` (Korean) specifies a **Python web application** that reads GoogleTest XML result
files produced by Jenkins builds and presents them through a browser dashboard: latest build summary,
pass/fail trend charts, per-module failure breakdown, and searchable/filterable test detail views.
`GoogleTestResults/` holds 100 synthetic GoogleTest XML files (10 Jenkins builds × 10 modules) that
the app must parse — this is the only input data source; there is no live Jenkins integration, no
XML mutation, and no auth.

Read `Requirements.md` in full before implementing — it defines exact page routes, field mappings,
status-precedence rules, and numeric acceptance criteria (e.g. build `10` must show 1,200 tests, 24
failures, 2.0% failure rate) that any implementation must reproduce against the current dataset.

## Data layout

- `GoogleTestResults/<build>/gtest_<module>.xml` — build folders `01`–`10` (Jenkins build numbers,
  sort numerically not lexically), each with one GoogleTest XML per module (10 modules).
- XML hierarchy: `testsuites > testsuite > properties/testcase > failure`. Per-suite `<properties>`
  carry `jenkins_build_number`, `module`, `source_file`, `tested_function`, and
  `target_build_failure_rate_percent` — these are the authoritative source for module/function
  names, not the suite or file name (see Requirements.md §4.3, FR-005).
- `GoogleTestResults/README.md` — human-readable summary of the dataset (per-build failure rates).
- `GoogleTestResults/generation_manifest.json` — machine-readable per-build stats (test/failure
  counts, timestamps) used to generate the synthetic data; useful for validating a parser's output.
- `TestCase_Template.xlsx` — manual test-case tracking template, unrelated to the XML parsing app.

## Key implementation rules from Requirements.md

These are easy to get wrong and are explicitly called out with acceptance criteria in the spec:

- **Status precedence**: when multiple status signals are present on one testcase, classify as
  `ERROR > FAILED > SKIPPED > DISABLED > PASSED`, in that priority order (FR-006).
- **Recompute aggregates from parsed records**, don't trust `<testsuites>`/`<testsuite>` declared
  `tests`/`failures`/`errors` attributes as-is — cross-check declared vs. actual counts and surface a
  warning (with XML path, declared value, computed value) on mismatch, but still render the
  parseable tests (FR-007, FR-008).
- **Failure rate**: `failures / total × 100`, rendered to 1 decimal place; if total is 0, display
  `N/A`, never `0` (FR-007).
- **Latest build** = max `jenkins_build_number`, falling back to numeric folder name, then timestamp,
  in that order (FR-009).
- **Module name fallback chain**: `property[name=module]` → first segment of `testcase@classname` →
  XML filename (FR-005).
- A single corrupt XML file must not take down the app — exclude it, show its path and parse error,
  and continue rendering results from the other 99 files (FR-035).
- Detail-page navigation back to a list view must preserve search/filter/sort/page state (FR-033).

## Verifying an implementation against the sample data

Requirements.md §7 gives fixed acceptance numbers for the current dataset — use these as smoke-test
targets:

- 10 builds, 100 XML files, 10 modules, 1,200 tests/build, 12,000 total test records.
- Latest build is `10`: 1,200 tests, 1,176 passed, 24 failed, 2.0% failure rate.
- Per-build failure rates in order (builds 01–10): 8%, 4%, 9%, 6%, 3%, 7%, 5%, 10%, 4%, 2%.
- Build 10 per-module breakdown (all modules have 120 tests): `ChildLockController` 3 failures,
  `CommunicationGateway` 3, `DiagnosticManager` 2, `DoorStateManager` 3, `LockActuator` 2,
  `PersistenceManager` 2, `SpeedInterlock` 3, `StateConsistencyMonitor` 2, `SwitchInput` 2,
  `VehicleSignalAdapter` 2.
