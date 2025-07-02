# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.formatter.code_parser import replace_comments

# MOCK: find_fucntion_start_line Implementation for pytest
def find_function_start_line(content, function_name, param_signature=None, occurrence=1):
    # seachring simple function name by name (simplified)
    lines = content.splitlines()
    for idx, line in enumerate(lines):
        if function_name in line and line.strip().endswith("{"):
            return idx
    return -1

# MOCK: header_comment_exists Implementation for pytest
def header_comment_exists(lines, start_line):
    # Checking if Doxygen_Comment exists above the function
    return start_line >= 1 and lines[start_line - 1].strip().startswith("///")

# MOCK: remove_existing_header Implementation for pytest
def remove_existing_header(lines, start_line):
    # Seaching backwards from the start_line and removing all Doxygen comment lines
    remove_start = start_line - 1
    while remove_start >= 0 and lines[remove_start].strip().startswith("///"):
        remove_start -= 1
    return lines[:remove_start + 1] + lines[start_line:]

# ------------------------------------------------------------------------
# Starting with test implementation
# ------------------------------------------------------------------------

def test_replace_comments_insert_new(tmp_path, monkeypatch):
    # Patch / Mock helper functions
    monkeypatch.setattr("src.formatter.code_parser.find_function_start_line", find_function_start_line)
    monkeypatch.setattr("src.formatter.code_parser.header_comment_exists", header_comment_exists)
    monkeypatch.setattr("src.formatter.code_parser.remove_existing_header", remove_existing_header)

    test_file = tmp_path / "test.cpp"
    test_file.write_text("""
int add(int a, int b) {
    return a + b;
}
""")

    functions = [{
        "name": "add",
        "params": "int a, int b",
        "count": 1,
        "doxygen": "/// Adds two integers.\n/// @param a First number\n/// @param b Second number\n/// @return Sum of a and b"
    }]

    replace_comments(str(test_file), functions)

    content = test_file.read_text()
    assert "/// Adds two integers." in content
    assert "int add(int a, int b)" in content
    assert functions[0]["startLine"] > 0

def test_replace_comments_replace_existing(tmp_path, monkeypatch):
    monkeypatch.setattr("src.formatter.code_parser.find_function_start_line", find_function_start_line)
    monkeypatch.setattr("src.formatter.code_parser.header_comment_exists", header_comment_exists)
    monkeypatch.setattr("src.formatter.code_parser.remove_existing_header", remove_existing_header)

    test_file = tmp_path / "test.cpp"
    test_file.write_text("""
/// Old comment
int subtract(int a, int b) {
    return a - b;
}
""")

    functions = [{
        "name": "subtract",
        "params": "int a, int b",
        "count": 1,
        "doxygen": "/// Subtracts b from a.\n/// @param a Minuend\n/// @param b Subtrahend\n/// @return Difference"
    }]

    replace_comments(str(test_file), functions)

    content = test_file.read_text()
    assert "/// Old comment" not in content
    assert "/// Subtracts b from a." in content
    assert functions[0]["startLine"] > 0