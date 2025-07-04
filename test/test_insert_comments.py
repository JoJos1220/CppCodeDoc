# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.formatter.code_parser import insert_comments

# MOCK extract_functions Implementation
def extract_functions(file_path):
    content = Path(file_path).read_text()
    funcs = []
    if "func1" in content:
        funcs.append({
            "name": "func1",
            "params": "",
            "count": 1,
            "comment": "",
            "isDoxygenComment": False,
        })
    if "func2" in content:
        funcs.append({
            "name": "func2",
            "params": "",
            "count": 1,
            "comment": "/// existierender Header",
            "isDoxygenComment": True,
        })
    return funcs

# MOCK find_function_start_line Implementation
def find_function_start_line(content, name, params, count):
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith(f"void {name}("):
            return i
    return -1

# MOCK header_comment_exists Implementation
def header_comment_exists(lines, start_line):
    # Adding "///" in previous line
    return start_line > 0 and lines[start_line-1].strip().startswith("///")

# MOCK add_header_comment Implementation
def add_header_comment(lines, func_name, start_line, comment_text=None):
    # Ading two space elements + default comment header
    comment = comment_text or f"// Header fuer {func_name}"
    insert_pos = start_line
    comment_lines = ["", ""] + [comment]
    return lines[:insert_pos] + comment_lines + lines[insert_pos:]

# MOCK remove_existing_header Implementation
def remove_existing_header(lines, start_line):
    # Deleting one line bevor start_line IF a comment is present
    if start_line > 0 and lines[start_line-1].strip().startswith("///"):
        return lines[:start_line-1] + lines[start_line:]
    return lines

# MOCK add_post_comment Implementation
def add_post_comment(lines, func_name, start_line):
    # Seachring closing "}" of the function (very roughly: next "}" after start_line)
    for i in range(start_line, len(lines)):
        if lines[i].strip() == "}":
            return lines[:i+1] + [f"// Post-Comment fuer {func_name}"] + lines[i+1:]
    return lines

# MOCK convert_doxygen_to_default_comment Implementation
def convert_doxygen_to_default_comment(comment):
    return comment.replace("///", "//")

# MOCK convert_single_line_comment_to_header Implementation
def convert_single_line_comment_to_header(lines, start_line):
    # Converting simple single-line comment to block comment
    i = start_line - 1
    if i >= 0 and lines[i].strip().startswith("//"):
        lines[i] = "/* " + lines[i].strip()[2:].strip() + " */"
    return lines

# ------------------------------------------------------------------------
# Setting up monkey patches
# ------------------------------------------------------------------------
mocks = {
    "src.formatter.code_parser.extract_functions": extract_functions,
    "src.formatter.code_parser.find_function_start_line": find_function_start_line,
    "src.formatter.code_parser.header_comment_exists": header_comment_exists,
    "src.formatter.code_parser.add_header_comment": add_header_comment,
    "src.formatter.code_parser.remove_existing_header": remove_existing_header,
    "src.formatter.code_parser.add_post_comment": add_post_comment,
    "src.formatter.code_parser.convert_doxygen_to_default_comment": convert_doxygen_to_default_comment,
    "src.formatter.code_parser.convert_single_line_comment_to_header": convert_single_line_comment_to_header,
}

def patch_functions(monkeypatch, mocks):
    for target, func in mocks.items():
        monkeypatch.setattr(target, func)


# ------------------------------------------------------------------------
# Starting with test implementation
# ------------------------------------------------------------------------

def test_insert_comments_inserts_header(tmp_path, monkeypatch):
    file = tmp_path / "test.cpp"
    file.write_text("void func1() {\n}\n")

    patch_functions(monkeypatch, mocks)

    insert_comments(str(file), {"headerCommentStyle": "default"})

    content = file.read_text()
    # Check if Pre-Comment with 2 spaces before func1 was inserted
    assert "// Header fuer func1" in content
    assert content.count("\n\n// Header fuer func1") == 1
    # Post-Comment added after "}"
    assert "// Post-Comment fuer func1" in content

def test_insert_comments_skips_existing_header(tmp_path, monkeypatch):
    file = tmp_path / "test.cpp"
    file.write_text("// existierender Header\nvoid func2() {\n}\n")

    patch_functions(monkeypatch, mocks)

    insert_comments(str(file), {"headerCommentStyle": "doxygen"})

    content = file.read_text()
    # existing header should NOT be changed and not doubled
    assert content.startswith("// existierender Header")
    # Post-Comment should exist
    assert "// Post-Comment fuer func2" in content

def test_insert_comments_multiple_functions(tmp_path, monkeypatch):
    file = tmp_path / "test.cpp"
    file.write_text("""
void func1() {
}

/// existierender Header
void func2() {
}
""")

    patch_functions(monkeypatch, mocks)
    insert_comments(str(file), {"headerCommentStyle": "default"})

    content = file.read_text()
    # func1: new header + Post-Comment
    assert "// Header fuer func1" in content
    assert "// Post-Comment fuer func1" in content
    # func2: existing Header stays, Post-Comment also
    assert "// existierender Header" in content
    assert "// Post-Comment fuer func2" in content