# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys
import os
import pytest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.formatter.doc_generator import generate_documentation

@pytest.fixture
def arguments(tmp_path):
    return {
        "readonly": False,
        "headerCommentStyle": "doxygen",
        "backup_path": str(tmp_path / "backup")
    }

@pytest.fixture
def source_files():
    return ["test.cpp"]

def test_generate_documentation_success(arguments, tmp_path):
    # Creating temp test.cpp-file
    test_file = tmp_path / "test.cpp"
    test_file.write_text("int main() { return 0; }")

    # Creating Backup-Directory
    backup_dir = Path(arguments["backup_path"])
    backup_dir.mkdir(parents=True, exist_ok=True)

    source_files = [str(test_file)]

    mock_functions = [{
        "name": "main",
        "params": "",
        "count": 1,
        "comment": "/*-----------------------------------------------------------------------------\n"
                " * main -->> TODO: Add your description here\n"
                " * ----------------------------------------------------------------------------\n*/",
        "return_type": "int",
        "const": False,
        "file": str(test_file),
        "startLine": 5,
        "isDoxygenComment": False,
        "doxygen": "/**\n"
                " * @brief main -->> TODO: Add your description here\n"
                " * @return TODO\n"
                " */",
        "isTemplate": False,
        "templateParams": None
    }]

    with patch("src.formatter.code_parser.extract_functions", return_value=mock_functions) as _, \
         patch("src.formatter.code_parser.insert_comments"), \
         patch("src.formatter.code_parser.replace_comments"), \
         patch("src.formatter.doxygen_generator.generate_doxygen_comment"):

        result = generate_documentation(arguments, source_files)
        assert result == mock_functions

        # Check, if Backup was created successfull
        backup_file = backup_dir / "test.cpp.bak"
        assert backup_file.exists()

def test_generate_documentation_readonly(arguments, tmp_path):
    test_file = tmp_path / "test.cpp"
    test_file.write_text("int main() { return 0; }")
    arguments["readonly"] = True
    source_files = [str(test_file)]

    mock_functions = [{
        "name": "main",
        "params": "",
        "count": 1,
        "comment": "",
        "return_type": "int",
        "const": False,
        "file": str(test_file),
        "startLine": 0,
        "isDoxygenComment": False,
        "doxygen": "/**\n"
                   " * @brief TODO main description.\n"
                   " * @return TODO\n"
                   " */",
        "isTemplate": False,
        "templateParams": None
    }]

    with patch("src.formatter.code_parser.extract_functions", return_value=[]), \
         patch("src.formatter.code_parser.insert_comments") as mock_insert, \
         patch("src.formatter.code_parser.replace_comments") as mock_replace, \
         patch("src.formatter.code_parser.make_file_backup") as mock_backup, \
         patch("src.formatter.doxygen_generator.generate_doxygen_comment"):
        result = generate_documentation(arguments, source_files)

    assert result == mock_functions
    mock_insert.assert_not_called()
    mock_replace.assert_not_called()
    mock_backup.assert_not_called()

def test_generate_documentation_backup_fails(arguments, tmp_path):
    test_file = tmp_path / "test.cpp"
    test_file.write_text("int main() { return 0; }")
    source_files = [str(test_file)]
    arguments["readonly"] = bool(False)

    expected_error = f"ERROR while creating Backupdir: {arguments['backup_path']}"

    with patch("src.formatter.doc_generator.make_file_backup", return_value=bool(False)), \
         patch("src.formatter.code_parser.insert_comments"), \
         patch("src.formatter.code_parser.extract_functions"), \
         patch("src.formatter.code_parser.replace_comments"), \
         patch("src.formatter.doxygen_generator.generate_doxygen_comment"):

        result = generate_documentation(arguments, source_files)
        assert result == expected_error