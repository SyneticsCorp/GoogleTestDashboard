"""!
@file test_config.py
@brief Unit tests for FR-001 result-path resolution (src/gtestdash/config.py).
"""
import os

import pytest

from gtestdash.config import ResultsPathError, resolveResultsPath


def test_resolveResultsPath_usesDefaultDirUnderWorkingDir(tmp_path):
    """!
    @brief With no configured path, the default "GoogleTestResults" folder under
           the working directory is used, per FR-001's default-value rule.
    """
    defaultDir = tmp_path / "GoogleTestResults"
    defaultDir.mkdir()

    resolvedPath = resolveResultsPath(configuredPath=None, workingDir=str(tmp_path))

    assert resolvedPath == str(defaultDir.resolve())


def test_resolveResultsPath_usesConfiguredPathWhenProvided(tmp_path):
    """!
    @brief A caller-supplied path is honored instead of the default, per FR-001.
    """
    customDir = tmp_path / "customResults"
    customDir.mkdir()

    resolvedPath = resolveResultsPath(configuredPath=str(customDir), workingDir=str(tmp_path))

    assert resolvedPath == str(customDir.resolve())


def test_resolveResultsPath_raisesWithReasonAndPath_whenPathMissing(tmp_path):
    """!
    @brief FR-001 requires the error to surface both the cause and the input
           path when the results root does not exist.
    """
    missingDir = str(tmp_path / "doesNotExist")

    with pytest.raises(ResultsPathError) as excInfo:
        resolveResultsPath(configuredPath=missingDir, workingDir=str(tmp_path))

    assert excInfo.value.inputPath == missingDir
    assert "not exist" in excInfo.value.reason
    assert missingDir in str(excInfo.value)


def test_resolveResultsPath_raisesWhenPathIsAFileNotDirectory(tmp_path):
    """!
    @brief A path that exists but is not a directory is also invalid input.
    """
    filePath = tmp_path / "notADirectory.txt"
    filePath.write_text("not a directory")

    with pytest.raises(ResultsPathError) as excInfo:
        resolveResultsPath(configuredPath=str(filePath), workingDir=str(tmp_path))

    assert excInfo.value.inputPath == str(filePath)
    assert "not a directory" in excInfo.value.reason
