# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

"""
Analyzing doxygen strings from comments.
"""

import re

def analyze_doxygen_todos(doxygen_comment: str):
    """
    analysing doxygen todos.
    """
    lines = doxygen_comment.splitlines()

    has_todo_in_brief, has_todo_in_return = False, False
    total_params, params_with_todo, total_tparams = 0, 0, 0
    tparams_with_todo, documented_blocks, open_todo_blocks = 0, 0, 0

    for line in lines:
        line = line.strip()

        if line.startswith("* @brief"):
            documented_blocks += 1
            if "TODO" in line:
                has_todo_in_brief = True
                open_todo_blocks += 1

        elif line.startswith("* @tparam"):
            documented_blocks += 1
            total_tparams += 1
            match = re.match(r"\* @tparam (\w+)\s+(.*)", line)
            if match:
                _, description = match.groups()
                if "TODO" in description:
                    tparams_with_todo += 1
                    open_todo_blocks += 1

        elif line.startswith("* @param"):
            documented_blocks += 1
            total_params += 1
            match = re.match(r"\* @param (\w+)\s+(.*)", line)
            if match:
                _, description = match.groups()
                if "TODO" in description:
                    params_with_todo += 1
                    open_todo_blocks += 1

        elif line.startswith("* @return"):
            documented_blocks += 1
            if "TODO" in line:
                has_todo_in_return = True
                open_todo_blocks += 1
    return {
        "documented_blocks": documented_blocks, # Total done comments
        "open_todo_blocks": open_todo_blocks,   # Total open comments
        "todo_in_brief": has_todo_in_brief,
        "todo_in_return": has_todo_in_return,
        "total_tparams": total_tparams,
        "tparams_with_todo": tparams_with_todo,
        "total_params": total_params,
        "params_with_todo": params_with_todo,
    }
