# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

"""
Calculation of open to-tods
"""


from generator.analyze_doxygen import analyze_doxygen_todos

def calculation_of_todos(functions):
    """
    calculation of overall to-dos within functions.
    """
    total_funcs = len(functions)
    todo_funcs = sum(1 for f in functions if "TODO" in f.get("doxygen", ""))
    done_funcs = total_funcs - todo_funcs
    percent_done = int((done_funcs / total_funcs) * 100) if total_funcs else 0

    return_todo, tparams_todo, params_todo = 0, 0, 0
    brief_todo, total_tparams, total_params = 0, 0, 0

    for func in functions:
        func["doxygen_TODO_Analyze"] = analyze_doxygen_todos(func.get("doxygen", ""))
        return_todo += int(func["doxygen_TODO_Analyze"]["todo_in_return"])
        tparams_todo += int(func["doxygen_TODO_Analyze"]["tparams_with_todo"])
        total_tparams += func["doxygen_TODO_Analyze"]["total_tparams"]
        params_todo += func["doxygen_TODO_Analyze"]["params_with_todo"]
        total_params += func["doxygen_TODO_Analyze"]["total_params"]
        brief_todo += int(func["doxygen_TODO_Analyze"]["todo_in_brief"])

    percent_brief_done = (
        int(((total_funcs - brief_todo) / total_funcs) * 100)
        if total_funcs else 0)
    percent_tparams_done = (
        int(((total_tparams - tparams_todo) / total_tparams) * 100)
        if total_tparams else 0)
    percent_params_done = (
        int(((total_params - params_todo) / total_params) * 100)
        if total_params else 0)
    percent_return_done = (
        int(((total_funcs - return_todo) / total_funcs) * 100)
        if total_funcs else 0)

    return {
        "total_funcs": total_funcs,
        "done_funcs": done_funcs,
        "percent_done": percent_done,
        "brief_done": total_funcs - brief_todo,
        "percent_brief_done": percent_brief_done,
        "tparams_done": total_tparams - tparams_todo,
        "total_tparams": total_tparams,
        "percent_tparams_done": percent_tparams_done,
        "params_done": total_params - params_todo,
        "total_params": total_params,
        "percent_params_done": percent_params_done,
        "return_done": total_funcs - return_todo,
        "percent_return_done": percent_return_done
    }
