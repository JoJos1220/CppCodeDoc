# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys, os, pytest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "src")))
from generator.calcToDos import calculation_of_todos


@pytest.fixture
def functions_input():
    return [
        {"name": "func1", "doxygen": "/// Brief\n/// TODO: implement\n/// @return int"},
        {"name": "func2", "doxygen": "/// Brief desc\n/// @param x desc\n/// @return int"},
        {"name": "func3", "doxygen": "/// TODO: brief\n/// @param x TODO\n/// @return TODO"},
    ]

@patch("generator.calcToDos.analyze_doxygen_todos")
def test_calculation_of_todos(mock_analyze, functions_input):
    mock_analyze.side_effect = [
        {"todo_in_return": 1, "tparams_with_todo": 0, "total_tparams": 0, "params_with_todo": 0, "total_params": 0, "todo_in_brief": 1},
        {"todo_in_return": 0, "tparams_with_todo": 0, "total_tparams": 0, "params_with_todo": 0, "total_params": 1, "todo_in_brief": 0},
        {"todo_in_return": 1, "tparams_with_todo": 0, "total_tparams": 0, "params_with_todo": 1, "total_params": 1, "todo_in_brief": 1}
    ]

    result = calculation_of_todos(functions_input)

    assert result == {
        "total_funcs": 3,
        "done_funcs": 1,
        "percent_done": 33,
        "brief_done": 1,
        "percent_brief_done": 33,
        "tparams_done": 0,
        "total_tparams": 0,
        "percent_tparams_done": 0,
        "params_done": 1,
        "total_params": 2,
        "percent_params_done": 50,
        "return_done": 1,
        "percent_return_done": 33,
    }