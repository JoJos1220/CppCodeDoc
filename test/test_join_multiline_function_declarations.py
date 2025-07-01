# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.formatter.code_parser import join_multiline_function_declarations

def test_join_simple_multiline_function():
    lines = [
        "int",
        "myFunction(",
        "int a, int b",
        ") {",
        "  return a + b;",
        "}"
    ]
    joined, mapping, _ = join_multiline_function_declarations(lines)
    assert "myFunction(" in joined[0] or "myFunction(" in joined[1]
    assert any("int a, int b" in line for line in joined)
    assert len(joined) == len(mapping)

def test_preserve_empty_lines():
    lines = [
        "",
        "int foo()",
        "{",
        "  return 42;",
        "}"
    ]
    joined, _, final_startlines = join_multiline_function_declarations(lines)
    assert joined[0] == "int foo() {"  # Empty line preserved
    assert len(joined) == 3
    assert final_startlines[0] == 1

def test_join_multiline_constructor_declaration():
    code = """\
class test{
    public:
        test() : operand1(0), operand2(0)
        {
            // Constructor implementation
        }
};
"""
    lines = code.splitlines()

    joined, _, _ = join_multiline_function_declarations(lines)

    # Appended constructor command line
    expected_joined_line = 'test() : operand1(0), operand2(0) {'

    # finding the line that starts with "test()" (the joined constructor line)
    found = any(expected_joined_line in line for line in joined)

    assert found, f"Appended constructor line could not be found.\nCurrent lines:\n{joined}"

def test_operator_overload_function():
    lines = [
        "class Vec2 {",
        "public:",
        "    Vec2 operator+ (const Vec2& other) const",
        "    {",
        "        return Vec2();",
        "    }",
        "};"
    ]
    joined, _, _ = join_multiline_function_declarations(lines)
    assert any("operator+" in line for line in joined)
    assert any("return Vec2();" in line for line in joined)

def test_multiple_functions_in_one_line():
    lines = [
        "int add(int a, int b) { return a + b; } int sub(int a, int b) { return a - b; }"
    ]
    joined, _, _ = join_multiline_function_declarations(lines)
    assert len(joined) == 4
    assert any("return a + b; }" in line for line in joined)

def test_ignores_define_lines():
    lines = [
        "#define PI 3.14",
        "double area(",
        "double r",
        ") {",
        "  return PI * r * r;",
        "}"
    ]
    joined, _, _ = join_multiline_function_declarations(lines)
    assert any("area(" in line for line in joined)
    assert any("return PI" in line for line in joined)

def test_multiline_with_comment_inside():
    lines = [
        "int multiply(",
        "int a, /* multiplier */",
        "int b",
        ") {",
        "    return a * b;",
        "}"
    ]
    joined, _, _ = join_multiline_function_declarations(lines)
    assert any("multiply(" in line for line in joined)
    assert any("return a * b;" in line for line in joined)

def test_declaration_only_should_not_join():
    lines = [
        "void notDefinedYet(",
        "int a, int b",
        ");"
    ]
    joined, _, _ = join_multiline_function_declarations(lines)
    assert any("notDefinedYet" in line for line in joined)
    assert all(not line.strip().endswith("{") for line in joined)

def test_nested_parentheses_in_arguments():
    lines = [
        "void doSomething(",
        "std::function<void(int)> callback = [](int x) { return x * 2; }",
        ") {",
        "  callback(21);",
        "}"
    ]
    joined, _, _ = join_multiline_function_declarations(lines)
    assert any("doSomething(" in line for line in joined)
    assert any("callback(21);" in line for line in joined)

def test_comment_at_end_of_function():
    lines = [
        "int foo(int a) { return a + 1; } // simple increment"
    ]
    joined, _, _ = join_multiline_function_declarations(lines)
    assert "foo" in joined[0]
    assert "// simple increment" in lines[0]

def test_function_with_near_preprocessor_directive():
    lines = [
        "#ifdef DEBUG",
        "void debugPrint() {",
        "  // do something",
        "}",
        "#endif"
    ]
    joined, _, _ = join_multiline_function_declarations(lines)
    assert any("debugPrint" in line for line in joined)

def test_namespace_qualified_method():
    lines = [
        "void myspace::MyClass::func(",
        "int a",
        ") {",
        "  return;",
        "}"
    ]
    joined, _, _ = join_multiline_function_declarations(lines)
    assert any("myspace::MyClass::func" in line for line in joined)

def test_visibility_modifiers_preserved():
    lines = [
        "class Test {",
        "public:",
        "    void foo();",
        "private:",
        "    int data;",
        "};"
    ]
    joined, _, _ = join_multiline_function_declarations(lines)
    assert "public:" in joined
    assert "private:" in joined

def test_function_closes_with_commend_bevor_opening_curly_brakets():
    lines = [
        "void dumpTestingFunction(int a, int _b) // Doing some strange Blabla for testing",
        "{",
        "  return a + _b;",
        "}"
    ]
    joined, _, _ = join_multiline_function_declarations(lines)
    assert "void dumpTestingFunction(int a, int _b) {" in joined
