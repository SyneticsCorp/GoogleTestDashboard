"""!
@file config.py
@brief GoogleTest results root path configuration (FR-001).

Resolves the directory the parsing layer will search for build folders and
GoogleTest XML files. The path is either supplied explicitly or defaults to
a "GoogleTestResults" folder under the current working directory.
"""
import os

## Default results folder name used when no path is configured (FR-001).
defaultResultsDirName = "GoogleTestResults"


class ResultsPathError(Exception):
    """!
    @brief Raised when the configured/default GoogleTest results path is invalid.

    Carries both the offending input path and a human-readable reason so the
    caller can display "오류 원인과 입력 경로" as required by FR-001's
    acceptance criterion.
    """

    def __init__(self, inputPath, reason):
        """!
        @brief Build the error with the input path and failure reason attached.
        @param inputPath Path string that failed validation.
        @param reason Short, human-readable explanation of why it failed.
        """
        self.inputPath = inputPath
        self.reason = reason
        super().__init__(f"Invalid GoogleTest results path '{inputPath}': {reason}")


def resolveResultsPath(configuredPath=None, workingDir=None):
    """!
    @brief Resolve the GoogleTest results root directory (FR-001).
    @param configuredPath Optional explicit path; when omitted, the default
           "GoogleTestResults" folder under workingDir is used.
    @param workingDir Base directory for the default path; defaults to the
           current process working directory.
    @return Absolute path string to an existing, validated directory.
    @throws ResultsPathError when the resolved path does not exist or is not
            a directory.
    """
    baseDir = workingDir if workingDir is not None else os.getcwd()
    candidatePath = configuredPath if configuredPath else os.path.join(baseDir, defaultResultsDirName)

    if not os.path.exists(candidatePath):
        raise ResultsPathError(candidatePath, "path does not exist")
    if not os.path.isdir(candidatePath):
        raise ResultsPathError(candidatePath, "path is not a directory")

    return os.path.abspath(candidatePath)
