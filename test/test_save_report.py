# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys, os, tempfile, pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.generator.save_report import save_documentation

# Dummy-Functions for testing
dummy_functions = [
    {
        "name": "add",
        "templateParams": "",
        "params": "int a, int b",
        "return_type": "int",
        "file": "test.c",
        "startLine": 42,
        "doxygen": "@brief Addiert zwei Zahlen\n@param a Erste Zahl\n@param b Zweite Zahl\n@return Summe",
    }
]

@pytest.mark.parametrize("formats", [["markdown"], ["html"], ["markdown", "html"]])
def test_save_documentation(formats):
    with tempfile.TemporaryDirectory() as tmpdir:
        output_base = os.path.join(tmpdir, "output")
        arguments = {
            "output_path": output_base,
            "output_format": formats,
            "document": {
                "title": "Test Report",
                "author": "Test Author",
                "date": "2025-06-16",
                "highlightTodo": False,
                "showDocProgress": True,
                "logoPath": None,
                "version": "1.0.0"
            },
            "app_info": {"version": "1.0.0"},
        }

        file_path, todo_stats = save_documentation(arguments, dummy_functions)

        # Check if file exists
        if "markdown" in formats or "md" in formats:
            assert os.path.isfile(output_base + ".md")
        if "html" in formats:
            assert os.path.isfile(output_base + ".html")

        # Checking return values
        assert isinstance(file_path, str)
        assert isinstance(todo_stats, dict)
        assert "percent_done" in todo_stats
