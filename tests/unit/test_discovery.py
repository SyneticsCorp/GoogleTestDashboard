"""!
@file test_discovery.py
@brief Unit tests for FR-002/FR-003 build/XML discovery (src/gtestdash/parsing/discovery.py).
"""
from gtestdash.parsing.discovery import findBuildFolders, findXmlFiles


def test_findBuildFolders_sortsNumericFolderNamesNumerically(tmp_path):
    """!
    @brief "09" must sort before "10" (numeric, not lexicographic) per FR-002.
    """
    for name in ["10", "02", "09", "01"]:
        (tmp_path / name).mkdir()

    builds = findBuildFolders(str(tmp_path))

    assert [build.folderName for build in builds] == ["01", "02", "09", "10"]


def test_findBuildFolders_ignoresFilesAtRoot(tmp_path):
    """!
    @brief Non-directory entries at the results root are not builds (FR-002).
    """
    (tmp_path / "01").mkdir()
    (tmp_path / "README.md").write_text("not a build folder")

    builds = findBuildFolders(str(tmp_path))

    assert [build.folderName for build in builds] == ["01"]


def test_findXmlFiles_findsXmlRecursivelyWithoutDuplicates(tmp_path):
    """!
    @brief Recursive search finds every .xml once, per FR-003.
    """
    nested = tmp_path / "sub"
    nested.mkdir()
    (tmp_path / "a.xml").write_text("<a/>")
    (nested / "b.xml").write_text("<b/>")
    (tmp_path / "notes.txt").write_text("ignore me")

    xmlFiles = findXmlFiles(str(tmp_path))

    assert sorted(xmlFiles) == sorted(
        [str(tmp_path / "a.xml"), str(nested / "b.xml")]
    )
