"""!
@file discovery.py
@brief Build-folder and XML-file discovery under the results root (FR-002, FR-003).
"""
import os

from gtestdash.parsing.models import BuildInfo


def _numericSortKey(folderName):
    """!
    @brief Sort key that orders numeric folder names by value, not lexically.
    @param folderName Folder name string (e.g. "01", "10", "release-a").
    @return Tuple placing numeric names before non-numeric ones, numeric-first.
    """
    if folderName.isdigit():
        return (0, int(folderName), folderName)
    return (1, 0, folderName)


def findBuildFolders(resultsRoot):
    """!
    @brief Discover build folders directly under the results root (FR-002).
    @param resultsRoot Absolute or relative path to the GoogleTest results root.
    @return List of BuildInfo, numeric folder names sorted numerically ("09"
            before "10"); non-numeric names sort after, alphabetically.
    """
    entries = os.listdir(resultsRoot)
    folderNames = [name for name in entries if os.path.isdir(os.path.join(resultsRoot, name))]
    folderNames.sort(key=_numericSortKey)
    return [BuildInfo(folderName=name, folderPath=os.path.join(resultsRoot, name)) for name in folderNames]


def findXmlFiles(buildFolder):
    """!
    @brief Recursively find every .xml file under a build folder (FR-003).
    @param buildFolder Path to one build folder.
    @return List of absolute-ish file paths, each XML file listed exactly once.
    """
    xmlPaths = []
    for currentDir, _subDirs, fileNames in os.walk(buildFolder):
        for fileName in fileNames:
            if fileName.lower().endswith(".xml"):
                xmlPaths.append(os.path.join(currentDir, fileName))
    return xmlPaths
