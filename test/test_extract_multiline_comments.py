# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.formatter.code_parser import extract_multiline_comments

def test_extract_single_multiline_comment():
    lines = [
        "int main() {",
        "   /* This is a",
        "      multi-line comment */",
        "   return 0;",
        "}"
    ]
    result = extract_multiline_comments(lines)
    assert len(result) == 1
    assert result[0][0] == 1  # Start line
    assert result[0][1] == 2  # End line
    assert "multi-line comment" in result[0][2]

def test_ignore_inline_comment():
    lines = [
        "int main() {",
        "   int x = 5; /* inline comment */",
        "   return x;",
        "}"
    ]
    result = extract_multiline_comments(lines)
    assert result == []  # Should ignore inline block comments