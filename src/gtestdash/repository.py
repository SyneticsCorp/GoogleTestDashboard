"""!
@file repository.py
@brief Assemble a full results Snapshot from the results root (FR-002~008).

Pure orchestration: discovery, parsing, and validation details all live in
gtestdash.parsing.*. This module only traverses build folders, delegates each
XML file to parseTestsuiteFile(), and assembles the outcome into a Snapshot.
"""
from dataclasses import dataclass, field

from gtestdash.parsing.discovery import findBuildFolders, findXmlFiles
from gtestdash.parsing.xml_parser import parseTestsuiteFile


@dataclass
class Snapshot:
    """!
    @brief Immutable-in-spirit result of one full results-tree scan.
    """

    ## All normalized ResultRecord across every parsable XML file.
    records: list = field(default_factory=list)
    ## Every ParseWarning raised while building this snapshot (FR-008, FR-035).
    warnings: list = field(default_factory=list)
    ## Paths of XML files excluded entirely due to a parse failure (FR-035).
    excludedFiles: list = field(default_factory=list)


def _absorbFileResult(records, warning, xmlPath, snapshot):
    """!
    @brief Fold one file's parse outcome into the snapshot being assembled.
    @param records ResultRecord list returned by parseTestsuiteFile() for xmlPath.
    @param warning ParseWarning or None, as returned alongside records.
    @param xmlPath Path of the XML file that produced this outcome.
    @param snapshot Snapshot being built; mutated in place.
    """
    if warning is not None:
        snapshot.warnings.append(warning)
        if not records:
            snapshot.excludedFiles.append(xmlPath)
    snapshot.records.extend(records)


def buildSnapshot(resultsRoot):
    """!
    @brief Discover every build folder's XML files and assemble one Snapshot.
    @param resultsRoot Path to the GoogleTest results root (see config.resolveResultsPath).
    @return Snapshot combining every parsable record, plus warnings and
            excluded files for anything that failed to parse (FR-035) or
            whose declared counts disagreed with the computed ones (FR-008).
    """
    snapshot = Snapshot()
    for buildInfo in findBuildFolders(resultsRoot):
        for xmlPath in findXmlFiles(buildInfo.folderPath):
            records, warning = parseTestsuiteFile(xmlPath)
            _absorbFileResult(records, warning, xmlPath, snapshot)
    return snapshot
