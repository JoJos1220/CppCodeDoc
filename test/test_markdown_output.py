# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys
import os
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.generator.markdown_output import write_markdown_doc

def test_write_markdown_doc_creates_expected_file():
    functions = [
        {
            "name": "add",
            "return_type": "int",
            "templateParams": "<Class T>",
            "params": "int a, int b",
            "file": "/path/to/file.c",
            "startLine": 42,
            "doxygen": "@brief Adds two numbers\n@param a First number\n@param b Second number\n@return Sum of a and b\n@see Nothing to see\n@note this is a note"
        }
    ]

    arguments = {
        "document": {
            "title": "My API",
            "version": "1.2.3",
            "author": "Test Author",
            "date": "2025-06-16",
            "highlightTodo": False,
            "showDocProgress": True,
            "logoPath": None
        },
        "app_info": {
            "version": "v5.0.0"
        }
    }

    todo_stats = {
        "total_funcs": 1,
        "done_funcs": 1,
        "percent_done": 100,
        "brief_done": 1,
        "percent_brief_done": 100,
        "tparams_done": 1,
        "total_tparams": 1,
        "percent_tparams_done": 100,
        "params_done": 2,
        "total_params": 2,
        "percent_params_done": 100,
        "return_done": 1,
        "percent_return_done": 100
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, "output.md")

        write_markdown_doc(functions, output_path, arguments, todo_stats)

        assert os.path.exists(output_path)

        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "# My API" in content
            assert "int add(<Class T>)(int a, int b)" in content
            assert "**🔹 Description:** Adds two numbers" in content
            assert "- **Parameter `a`**: First number" in content
            assert "- **Parameter `b`**: Second number" in content
            assert "**🔁 Return value:** Sum of a and b" in content
            assert "- **See:** Nothing to see" in content
            assert "> 💡 **Note:** this is a note" in content
            assert "SW-Version: v5.0.0" in content
