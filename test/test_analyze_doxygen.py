# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.generator.analyze_doxygen import analyze_doxygen_todos

def test_empty_comment():
    comment = ""
    result = analyze_doxygen_todos(comment)
    assert result == {
        "documented_blocks": 0,
        "open_todo_blocks": 0,
        "todo_in_brief": False,
        "todo_in_return": False,
        "total_params": 0,
        "params_with_todo": 0,
        "total_tparams": 0,
        "tparams_with_todo": 0,
    }

def test_comment_without_todo():
    comment = """/**
     * @brief This function does something useful
     * @param input An integer value
     * @return A result
     */"""
    result = analyze_doxygen_todos(comment)
    assert result == {
        "documented_blocks": 3,
        "open_todo_blocks": 0,
        "todo_in_brief": False,
        "todo_in_return": False,
        "total_params": 1,
        "params_with_todo": 0,
        "total_tparams": 0,
        "tparams_with_todo": 0,
    }

def test_todo_in_brief():
    comment = """/**
     * @brief TODO: implement this
     * @tparam T TODO: not implemented
     * @return Something
     */"""
    result = analyze_doxygen_todos(comment)
    assert result == {
        "documented_blocks": 3,
        "open_todo_blocks": 2,
        "todo_in_brief": True,
        "todo_in_return": False,
        "total_params": 0,
        "params_with_todo": 0,
        "total_tparams": 1,
        "tparams_with_todo": 1,
    }

def test_todo_in_return():
    comment = """/**
     * @brief Brief description
     * @return TODO: Return value to be defined
     */"""
    result = analyze_doxygen_todos(comment)
    assert result == {
        "documented_blocks": 2,
        "open_todo_blocks": 1,
        "todo_in_brief": False,
        "todo_in_return": True,
        "total_params": 0,
        "params_with_todo": 0,
        "total_tparams": 0,
        "tparams_with_todo": 0,
    }

def test_todo_in_param():
    comment = """/**
     * @brief Description
     * @tparam NoneSenseParam - I am descriped!
     * @param input TODO: describe parameter
     * @return A value
     */"""
    result = analyze_doxygen_todos(comment)
    assert result == {
        "documented_blocks": 4,
        "open_todo_blocks": 1,
        "todo_in_brief": False,
        "todo_in_return": False,
        "total_params": 1,
        "params_with_todo": 1,
        "total_tparams": 1,
        "tparams_with_todo": 0,
    }

def test_multiple_todos():
    comment = """/**
     * @brief TODO: main logic
     * @param a TODO: input a
     * @param b input b
     * @return TODO: result
     */"""
    result = analyze_doxygen_todos(comment)
    assert result == {
        "documented_blocks": 4,
        "open_todo_blocks": 3,
        "todo_in_brief": True,
        "todo_in_return": True,
        "total_params": 2,
        "params_with_todo": 1,
        "total_tparams": 0,
        "tparams_with_todo": 0,
    }
