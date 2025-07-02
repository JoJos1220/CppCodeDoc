# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.formatter.code_parser import extract_comment_for_function

def test_extract_multiline_comment():
    # Test, if multiline comment is extracted correctly
    lines = [
        "void someFunction() {",
        "    // some code",
        "}",
        "/* This is a",
        "   multi-line",
        "   comment */"
    ]
    orig_idx = 0  # FunctionIndex
    multiline_comments = [
        (3, 5, "This is a\nmulti-line\ncomment")  # Multiline comment starting at line 3
    ]
    comment = extract_comment_for_function(lines, orig_idx, multiline_comments)
    assert comment == ""

def test_extract_single_line_comment():
    # Test, if single line comment is extracted correctly
    lines = [
        "// NothingToExtractHere",
        "void someFunction() {",
        "    // some code",
        "    // another line of code",
        "}",
    ]
    orig_idx = 1  # index of the function
    multiline_comments = []  # No Blockcomment
    comment = extract_comment_for_function(lines, orig_idx, multiline_comments)
    assert comment == "// NothingToExtractHere"

def test_extract_no_comment():
    # Testing, if ther is no comment
    lines = [
        "void someFunction() {",
        "    // some code",
        "}",
    ]
    orig_idx = 0  # function index
    multiline_comments = []  # no block comment
    comment = extract_comment_for_function(lines, orig_idx, multiline_comments)
    assert comment == ""

    orig_idx = 1 # retesting with other start index
    comment = extract_comment_for_function(lines, orig_idx, multiline_comments)
    assert comment == ""
