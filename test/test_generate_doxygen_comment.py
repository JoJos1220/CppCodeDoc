# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.formatter.doxygen_generator import generate_doxygen_comment

def test_generate_doxygen_with_existing_doxygen_comment():
    func = {
        "name": "myFunction",
        "params": "int a, float b",
        "return_type": "int",
        "comment": """
        /**
         * @brief Adds two numbers.
         * @param a First number
         * @param b Second number
         * @return Sum of numbers
         */
        """,
        "isDoxygenComment": True,
        "isTemplate": False,
        "templateParams": None
    }

    generate_doxygen_comment(func)

    expected = (
        "/**\n"
        " * @brief Adds two numbers.\n"
        " * @param a First number\n"
        " * @param b Second number\n"
        " * @return Sum of numbers\n"
        " */"
    )

    assert func["doxygen"] == expected

def test_generate_doxygen_no_comment():
    func = {
        "name": "doStuff",
        "params": "void",
        "return_type": "void",
        "comment": "",
        "isDoxygenComment": False,
        "isTemplate": True,
        "templateParams": "<class T>"
    }

    generate_doxygen_comment(func)

    assert "@brief TODO doStuff description." in func["doxygen"]
    assert "@tparam T TODO" in func["doxygen"]
    assert "@param void" not in func["doxygen"]
    assert "@return" not in func["doxygen"]

def test_generate_doxygen_with_non_doxygen_comment():
    func = {
        "name": "multiply",
        "params": "int x, int y",
        "return_type": "int",
        "comment": """
        // Multiplies two numbers
        // and returns the result
        """,
        "isDoxygenComment": False
    }

    generate_doxygen_comment(func)

    assert "Multiplies two numbers" in func["doxygen"]
    assert "@param x TODO" in func["doxygen"]
    assert "@param y TODO" in func["doxygen"]
    assert "@return TODO" in func["doxygen"]

def test_generate_doxygen_with_template_params():
    func = {
        "name": "storeData",
        "params": "const std::map<std::string, std::vector<uint8_t>>& storage, int mode = 7000, float value",
        "return_type": "bool",
        "comment": "",
        "isDoxygenComment": False
    }

    generate_doxygen_comment(func)

    assert "@param storage TODO" in func["doxygen"]
    assert "@param mode TODO – default value if not overloaded: 7000" in func["doxygen"]
    assert "@param value TODO - default value if not overloaded" not in func["doxygen"]
    assert "@return TODO" in func["doxygen"]

def test_generate_doxygen_return_type_void_static():
    func = {
        "name": "reset",
        "params": "",
        "return_type": "static void",
        "comment": "",
        "isDoxygenComment": False
    }

    generate_doxygen_comment(func)

    assert "@return" not in func["doxygen"]

def test_generate_doxygen_with_function_default_parameters():
    func = {
        "name": "test",
        "params": "const char* type, uint8_t *payload = NULL, size_t _size = 0",
        "return_type": "int",
        "comment": "",
        "isDoxygenComment": False
    }

    generate_doxygen_comment(func)

    assert "@param type TODO" in func["doxygen"]
    assert "@param payload TODO – default value if not overloaded: NULL" in func["doxygen"]
    assert "@param _size TODO – default value if not overloaded: 0" in func["doxygen"]

def test_generate_doxygen_with_function_pointer_parameters():
    func = {
        "name": "SSEWrapper::setup",
        "params": "void (*SSEhandleRequest)(AsyncWebServerRequest *request)",
        "return_type": "void",
        "comment": "'/*-----------------------------------------------------------------------------\n * SSEWrapper::setup -->> TODO: Add your description here\n * ----------------------------------------------------------------------------\n*/'",
        "isDoxygenComment": False
    }

    generate_doxygen_comment(func)

    assert "@param SSEhandleRequest" in func["doxygen"]

def test_generate_doxygen_with_function_pointer_with_params():
    func = {
        "name": "setHandler",
        "params": "void (*handler)(int code, const std::string& message)",
        "return_type": "void",
        "comment": "",
        "isDoxygenComment": False
    }

    generate_doxygen_comment(func)

    assert "@param handler TODO (internal function parameter: int code, const std::string& message)" in func["doxygen"]


def test_generate_doxygen_with_extended_doxygen_tags():
    func = {
        "name": "testfunc",
        "params": "string nonesense",
        "return_type": "int",
        "comment": """
        /**
         * @brief Just for testing.
         * @brief second brief line
         * @param nonesense it is just nonsense
         * @return blabla if its not blabla
         * @return not blabla if it is blabla
         * @see it is Nonsense!
         * @note This is a note
         * @description This is a description that should not be used
         */
        """,
        "isDoxygenComment": True,
        "isTemplate": False,
        "templateParams": None
    }

    generate_doxygen_comment(func)

    expected = (
        "/**\n"
        " * @brief Just for testing.\n"
        " *        second brief line\n"
        " * @param nonesense it is just nonsense\n"
        " * @return blabla if its not blabla\n"
        " *         not blabla if it is blabla\n"
        " * @note This is a note\n"
        " * @see it is Nonsense!\n"
        " * @description This is a description that should not be used\n"
        " */"
    )

    assert func["doxygen"] == expected