# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys, os, tempfile
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.generator.html_output import write_html_doc

def test_write_html_doc_creates_expected_output():
    functions = [
        {
            "name": "add",
            "tparams": "",
            "params": "int a, int b",
            "return_type": "int",
            "doxygen": "@brief Adds two numbers\n@param a First number\n@param b Second number\n@return The sum",
            "file": "/some/path/math.c",
            "startLine": 42
        },
        {
            "name": "subtract",
            "tparams": "",
            "params": "int a, int b",
            "return_type": "int",
            "doxygen": "TODO: implement subtraction\n@param a First\n@param b Second",
            "file": "/some/path/math.c",
            "startLine": 87
        }
    ]

    arguments = {
        "document": {
            "title": "Math Functions",
            "author": "Tester",
            "date": "2025-06-16",
            "version": "1.0",
            "highlightTodo": True,
            "showDocProgress": True
        },
        "app_info": {
            "version": "1.2.3"
        }
    }

    todo_stats = {
        "done_funcs": 1,
        "total_funcs": 2,
        "percent_done": 50,
        "brief_done": 1,
        "percent_brief_done": 50,
        "tparams_done": 0,
        "total_tparams": 0,
        "percent_tparams_done": 0,
        "params_done": 3,
        "total_params": 4,
        "percent_params_done": 75,
        "return_done": 1,
        "percent_return_done": 50,
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = Path(tmpdir) / "doc.html"
        write_html_doc(functions, out_file, arguments, todo_stats)

        assert out_file.exists()

        content = out_file.read_text(encoding="utf-8")

        # Check for specific known strings
        assert "Math Functions" in content
        assert "add(int a, int b)" in content
        assert "subtract(int a, int b)" in content
        assert "TODO" in content  # because highlightTodo = True
        assert "50%" in content  # from the progress bars
        assert "@brief" in content
        assert "📘 Hide comments" in content
