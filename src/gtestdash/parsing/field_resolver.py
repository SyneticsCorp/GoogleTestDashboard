"""!
@file field_resolver.py
@brief Module/function identification with fallback chains (FR-005).
"""
import os


def extractProperties(testsuiteElement):
    """!
    @brief Read a <testsuite>'s <properties> into a name→value dict.
    @param testsuiteElement xml.etree.ElementTree.Element for a <testsuite>.
    @return Dict mapping property name to its "value" attribute; empty dict
            when the suite has no <properties> block.
    """
    propertiesDict = {}
    propertiesElement = testsuiteElement.find("properties")
    if propertiesElement is None:
        return propertiesDict
    for propertyElement in propertiesElement.findall("property"):
        propertyName = propertyElement.get("name")
        propertiesDict[propertyName] = propertyElement.get("value")
    return propertiesDict


def resolveModule(properties, testcaseElement, xmlPath):
    """!
    @brief Resolve module name via property → classname → file-name fallback (FR-005).
    @param properties Dict from extractProperties().
    @param testcaseElement xml.etree.ElementTree.Element for a <testcase>.
    @param xmlPath Path to the source XML file, used as the last-resort fallback.
    @return Module name string, from the highest-priority source available.
    """
    declaredModule = properties.get("module")
    if declaredModule:
        return declaredModule

    classname = testcaseElement.get("classname")
    if classname:
        return classname.split(".")[0]

    fileBaseName = os.path.splitext(os.path.basename(xmlPath))[0]
    return fileBaseName


def resolveFunction(properties, testcaseElement):
    """!
    @brief Resolve tested function via property → test-name-derived fallback (FR-005).
    @param properties Dict from extractProperties().
    @param testcaseElement xml.etree.ElementTree.Element for a <testcase>.
    @return Function name string, or a candidate derived from the test name's
            first underscore-separated segment when no property is declared.
    """
    testedFunction = properties.get("tested_function")
    if testedFunction:
        return testedFunction

    testName = testcaseElement.get("name") or ""
    return testName.split("_", 1)[0]
