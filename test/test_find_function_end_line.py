# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.formatter.code_parser import find_function_end_line

def test_find_function_end_line_multiline():
    code = """\
bool exampleFunction(
    int a,
    float b
) 
{
    if (a > 0) {
        a--;
    }
    return true;
}
"""
    lines = code.splitlines()
    assert find_function_end_line(lines, 0) == 9


def test_simple_function():
    code = """\
void hello() {
    printf("Hello World");
}
"""
    lines = code.splitlines()
    assert find_function_end_line(lines, 0) == 2


def test_function_with_nested_blocks():
    code = """\
int compute(int x) {
    if (x > 0) {
        while (x--) {
            printf("%d", x);
        }
    }
    return x;
}
"""
    lines = code.splitlines()
    assert find_function_end_line(lines, 0) == 7

def test_function_with_braces_in_string():
    code = """\
void logMessage() {
    const char* msg = "This { is not a real brace }";
    printf("%s", msg);
}
"""
    lines = code.splitlines()
    assert find_function_end_line(lines, 0) == 3

def test_function_with_unclosed_brace():
    code = """\
void broken() {
    if (true) {
        // missing closing brace
"""
    lines = code.splitlines()
    assert find_function_end_line(lines, 0) is None

def test_function_with_multiple_closing_braces_on_same_line():
    code = """\
void messy() {
    if (true) { doSomething(); }}
"""
    lines = code.splitlines()
    assert find_function_end_line(lines, 0) == 1

def test_empty_function_body():
    code = """\
void empty() {
}
"""
    lines = code.splitlines()
    assert find_function_end_line(lines, 0) == 1

def test_bracket_open_close_inline():
    code = """\
void none() {}
"""
    lines = code.splitlines()
    assert find_function_end_line(lines, 0) == 0

def test_bracket_open_close_in_same_line():
    code = """\
// Nothing to do at here
// another nochting to do here
/**
* @brief blabla
*/
void ThisIsMySuperComplexFunction() {
    // Within this function i am searching for {
    // and for }
    for (int i = 0; i < 10; i++) {
        if(i == "}" || i == "}") {
            // do nothing!!!
        }
    } 
}  

// Just an ending comment to check if funtion
// detects the endline correctly!
void anotherFunction() {}
"""
    lines = code.splitlines()
    assert find_function_end_line(lines, 5) == 13

def test_function_with_commented_braces():
    code = """\
void OLEDMainMenu(int _selected){
    // looping oled function
    if(getMenu() == MENUMAIN){       
    }/*else if(getMenu() == MENUACCSETTING){
        Not in Included!
    }*//*else if(getMenu() == MENUSPEEDSETTING){
         Not Included!
    }*/else if(getMenu() == MENUTESTSCREENSHOT){             
    }
} // OLEDMainMenu()
"""

    lines = code.splitlines()
    assert find_function_end_line(lines, 0) == 9
