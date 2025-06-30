# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import os, sys, pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.formatter.code_parser import check_input_string_looks_like_path

@pytest.mark.parametrize("path_str, expected", [
    ("../relative/path", True),
    ("folder/subfolder", True),
    ("./backupdir", True),
    ("backup", False),
    ("file.txt", False),
    (".hiddenfile", False),
    ("", False),
    (" ", False),
    ("a", False),
    ("ab", False),
    ("./folder/file.tar.gz", False),
    (None, False),
    (123, False),
    (["/fake/path"], False),
])
def test_cross_platform_paths(path_str, expected):
    assert check_input_string_looks_like_path(path_str) == expected

# windows specific-tests
@pytest.mark.parametrize("path_str, expected", [
    ("C:/BackupFolder", True),
    ("C:\\Users\\user\\backup", True),
    ("C:", False),
    ("C:/backup/file.txt", False),
])
def test_windows_paths(path_str, expected):
    if sys.platform != "win32":
        pytest.skip("Calling only on WINDOWS environement")
    assert check_input_string_looks_like_path(path_str) == expected


# Linux/macOS-specific tests
@pytest.mark.parametrize("path_str, expected", [
    ("/usr/local/backup", True),
    ("/some/dir/config.ini", False),
])
def test_unix_paths(path_str, expected):
    if sys.platform == "win32":
        pytest.skip("Calling only on Linux/macOS environement")
    assert check_input_string_looks_like_path(path_str) == expected
