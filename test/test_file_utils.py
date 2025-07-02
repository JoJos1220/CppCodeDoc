# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.utils.file_utils import get_cpp_files

def test_single_cpp_file(tmp_path):
    test_file = tmp_path / "main.cpp"
    test_file.write_text("int main() { return 0; }")

    result = get_cpp_files(str(test_file), {"recursive": False})
    assert result == [str(test_file)]

def test_single_non_cpp_file(tmp_path):
    test_file = tmp_path / "README.md"
    test_file.write_text("# This is a readme")

    result = get_cpp_files(str(test_file), {"recursive": False})
    assert result == []

def test_non_recursive_directory(tmp_path):
    (tmp_path / "file1.cpp").write_text("// file1")
    (tmp_path / "file2.h").write_text("// file2")
    (tmp_path / "file3.txt").write_text("not code")
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "file4.cpp").write_text("// file4")

    result = get_cpp_files(str(tmp_path), {"recursive": False})
    expected = [
        str(tmp_path / "file1.cpp"),
        str(tmp_path / "file2.h"),
    ]
    assert sorted(result) == sorted(expected)

def test_recursive_directory(tmp_path):
    (tmp_path / "file1.cpp").write_text("// file1")
    (tmp_path / "file2.hpp").write_text("// file2")
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "file3.ino").write_text("// Arduino")
    (subdir / "file4.txt").write_text("not relevant")

    result = get_cpp_files(str(tmp_path), {"recursive": True})
    expected = [
        str(tmp_path / "file1.cpp"),
        str(tmp_path / "file2.hpp"),
        str(subdir / "file3.ino"),
    ]
    assert sorted(result) == sorted(expected)

def test_path_is_neither_file_nor_directory():
    result = get_cpp_files("nonexistent_path_12345", {"recursive": True})
    assert result == []
