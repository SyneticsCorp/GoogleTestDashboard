"""!
@file test_field_resolver.py
@brief Unit tests for FR-005 module/function fallback resolution
       (src/gtestdash/parsing/field_resolver.py).

Uses edge-case fixtures in tests/fixtures/edge_cases/ that intentionally omit
the module property (and, in one case, the classname) since the real
GoogleTestResults dataset (read-only) always has both.
"""
import os
import xml.etree.ElementTree as elementTree

from gtestdash.parsing.field_resolver import extractProperties, resolveFunction, resolveModule

_fixtureDir = os.path.join(os.path.dirname(__file__), "..", "fixtures", "edge_cases")


def _loadSuiteAndCase(fixtureFileName):
    """!
    @brief Parse a fixture and return its lone (testsuite, testcase) pair.
    @param fixtureFileName Fixture file name under tests/fixtures/edge_cases/.
    @return Tuple of (testsuiteElement, testcaseElement).
    """
    tree = elementTree.parse(os.path.join(_fixtureDir, fixtureFileName))
    testsuite = tree.getroot().find("testsuite")
    testcase = testsuite.find("testcase")
    return testsuite, testcase


def test_resolveModule_usesModulePropertyWhenPresent():
    """!
    @brief property[name=module] wins over any fallback, per FR-005.
    """
    testsuite, testcase = _loadSuiteAndCase("missing_module_property.xml")
    properties = extractProperties(testsuite)
    properties["module"] = "ExplicitModule"

    assert resolveModule(properties, testcase, "irrelevant.xml") == "ExplicitModule"


def test_resolveModule_fallsBackToClassnameFirstSegment_whenModuleMissing():
    """!
    @brief No module property: fall back to classname's first "." segment (FR-005).
    """
    testsuite, testcase = _loadSuiteAndCase("missing_module_property.xml")
    properties = extractProperties(testsuite)

    assert "module" not in properties
    assert resolveModule(properties, testcase, "irrelevant.xml") == "FallbackModuleFromClassname"


def test_resolveModule_fallsBackToXmlFileName_whenModuleAndClassnameMissing():
    """!
    @brief No module property and no classname: fall back to the XML file name (FR-005).
    """
    testsuite, testcase = _loadSuiteAndCase("missing_module_and_classname.xml")
    properties = extractProperties(testsuite)

    assert resolveModule(properties, testcase, "/results/10/gtest_orphan.xml") == "gtest_orphan"


def test_resolveFunction_usesTestedFunctionPropertyWhenPresent():
    """!
    @brief property[name=tested_function] wins over any fallback (FR-005).
    """
    testsuite, testcase = _loadSuiteAndCase("missing_module_property.xml")
    properties = extractProperties(testsuite)

    assert resolveFunction(properties, testcase) == "DoSomething"


def test_resolveFunction_derivesCandidateFromTestName_whenPropertyMissing():
    """!
    @brief No tested_function property: derive a candidate from the test name (FR-005).
    """
    testsuite, testcase = _loadSuiteAndCase("missing_module_and_classname.xml")
    properties = extractProperties(testsuite)

    assert "tested_function" not in properties
    assert resolveFunction(properties, testcase) == "StandaloneCase"
