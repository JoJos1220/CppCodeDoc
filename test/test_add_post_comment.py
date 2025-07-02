# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.formatter.code_parser import add_post_comment

@patch("src.formatter.code_parser.find_function_end_line")
def test_post_comment_added_correctly(mock_find_end_line):
    lines = [
        "void test() {",
        "  int x = 42;",
        "}"  # <- Comment will be added here
    ]
    mock_find_end_line.return_value = 2
    expected = [
        "void test() {",
        "  int x = 42;",
        "} /* test() */"
    ]
    updated = add_post_comment(lines[:], "test", 0)
    assert updated == expected

@patch("src.formatter.code_parser.find_function_end_line")
def test_post_comment_removes_inline_comment(mock_find_end_line):
    lines = [
        "void compute() {",
        "  return;",
        "} // old comment"
    ]
    mock_find_end_line.return_value = 2
    expected = [
        "void compute() {",
        "  return;", 
        "} /* old comment */"
    ]
    updated = add_post_comment(lines[:], "compute", 0)
    assert updated == expected

@patch("src.formatter.code_parser.find_function_end_line")
def test_no_end_line_found(mock_find_end_line):
    lines = [
        "int incomplete(",
        "  int a"  # no closing function
    ]
    mock_find_end_line.return_value = None
    updated = add_post_comment(lines[:], "incomplete", 0)
    assert updated == lines  # should be unchanged

@patch("src.formatter.code_parser.find_function_end_line")
def test_multiline_block_comment_is_preserved(mock_find_end_line):
    lines = [
        "void example() {",
        "  doSomething();",
        "} /* old comment"
        " continues here */"
    ]
    mock_find_end_line.return_value = 2
    expected = lines[:]  # will be the same!
    updated = add_post_comment(lines[:], "example", 0)
    assert updated == expected

@patch("src.formatter.code_parser.find_function_end_line")
def test_comment_on_next_line_after_closing_brace(mock_find_end_line):
    lines = [
        "void process() {",
        "  execute();",
        "}",                         # ← curly bracket without comment
        "// previously on next line"
    ]
    mock_find_end_line.return_value = 2
    expected = [
        "void process() {",
        "  execute();",
        "} /* process() */",
        "// previously on next line"
    ]
    updated = add_post_comment(lines[:], "process", 0)
    assert updated == expected

@patch("src.formatter.code_parser.find_function_end_line")
def test_multilin_comment_on_next_line_after_closing_brace(mock_find_end_line):
    lines = [
        "void processTest() {",
        "  execute();",
        "}",                         # ← curly bracket without commend
        "/*next line",
        "  multiline comment */"
    ]
    mock_find_end_line.return_value = 2
    expected = [
        "void processTest() {",
        "  execute();",
        "} /* processTest() */",
        "/*next line",
        "  multiline comment */"
    ]
    updated = add_post_comment(lines[:], "processTest", 0)
    assert updated == expected
