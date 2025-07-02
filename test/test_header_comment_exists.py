# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.formatter.code_parser import header_comment_exists

def test_valid_header_comment():
    lines = [
        "/*",
        " * Dies ist ein Header-Kommentar",
        " */",
        "void meineFunktion() {",
        "    // Logik",
        "}"
    ]
    assert header_comment_exists(lines, 3) is True

def test_no_comment():
    lines = [
        "int x = 0;",
        "",
        "void test() {}",
    ]
    assert header_comment_exists(lines, 2) is False

def test_comment_too_far():
    lines = [
        "/* Kommentar */",
        "",
        "void test() {}",
    ]
    assert header_comment_exists(lines, 2) is False

def test_footer_comment_instead_of_header():
    lines = [
        "void test() {",
        "    // Logik",
        "}",
        "/* Kommentar nach der Funktion */"
    ]
    assert header_comment_exists(lines, 0) is False  # func_start = 0, should return False

def test_footer_disguised_as_header():
    lines = [
        "}",
        "/* Kommentar */",
        "void test() {"
    ]
    assert header_comment_exists(lines, 2) is False

def test_inline_comment_before_function():
    lines = [
        "// Einzeilige Info",
        "void test() {}"
    ]
    assert header_comment_exists(lines, 1) is True

def test_multiline_without_block_start():
    lines = [
        "// Kommentarzeile 1",
        "// Kommentarzeile 2",
        "void test() {}"
    ]
    assert header_comment_exists(lines, 2) is True

def test_single_line_command_with_empty_line():
    lines = [
        "// Kommentarzeile 1",
        "",
        "void test() {}"
    ]
    assert header_comment_exists(lines, 2) is False

def test_ifdef_block_with_duplicate_function():
    lines = [
        "/**",
        " * @brief Kommentar",
        " * @param void",
        " */",
        "#if !defined(NATIVE_ENVIRONMENT)",
        "void ESPFlashDebuggingFunction(void){",
        "  // body",
        "}/* ESPFlashDebuggingFunction() */",
        "#else",
        "void ESPFlashDebuggingFunction(void){;};/* ESPFlashDebuggingFunction() */",
        "#endif"
    ]
    # First Variant (#if-Path)
    assert header_comment_exists(lines, 5) is True
    # Second Variant (#else-Path)
    assert header_comment_exists(lines, 9) is False