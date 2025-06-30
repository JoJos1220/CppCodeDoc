# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import os

from generator.markdown_output import write_markdown_doc
from generator.html_output import write_html_doc
from generator.calcToDos import calculation_of_todos

def save_documentation(arguments, all_functions):
    output_dir = os.path.dirname(arguments["output_path"])
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_path = ""
    todo_stats = calculation_of_todos(all_functions)
    for format in arguments["output_format"]:
        file_path = ""
        if format == "markdown" or format == "md":
            file_path = f"{arguments['output_path']}.md"
            write_markdown_doc(all_functions, file_path, arguments, todo_stats)
        elif format == "html":
            file_path = f"{arguments['output_path']}.html"
            write_html_doc(all_functions, file_path, arguments, todo_stats)
        else:
            print(f"❌ Invalid Output Format: {format}")
            raise ValueError(f"Invalid Output Format: {format}")
        
    return file_path, todo_stats
