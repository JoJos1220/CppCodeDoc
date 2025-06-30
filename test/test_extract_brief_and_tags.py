# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.formatter.doxygen_generator import extract_brief_and_tags 

def test_extract_brief_and_tags_multiline():
    body_lines = [
        "@brief This function does something important",
        "       that spans across multiple lines",
        "@param key The unique key to identify the entry",
        "           which should not contain spaces.",
        "@tparam template value",
        "@param value The value to be stored.",
        "@return An error code",
        "        indicating success or failure.",
        "@note Internal note about the function",
        "        Nothing to say about that!"
    ]

    brief, param_docs, return_doc, notes_doc, tparam_doc, _ = extract_brief_and_tags(body_lines)

    expected_brief = (
        "This function does something important\n"
        " *        that spans across multiple lines"
    )
    expected_tparam_docs = {
        "template": "value"
    }
    expected_param_docs = {
        "key": "The unique key to identify the entry\n"
               " *        which should not contain spaces.",
        "value": "The value to be stored."
    }
    expected_return = ("An error code\n" 
                      " *         indicating success or failure."
    )
    expected_note= (
        "Internal note about the function\n"
        " *        Nothing to say about that!"
    )

    assert brief == expected_brief, f"Error: The brief text does not match! Expected: {expected_brief}, but got: {brief}"
    assert tparam_doc == expected_tparam_docs, f"Error: The tparam_doc does not match! Expected: {expected_tparam_docs}, but got: {tparam_doc}"
    assert param_docs == expected_param_docs, f"Error: The param_docs do not match! Expected: {expected_param_docs}, but got: {param_docs}"
    assert return_doc == expected_return, f"Error: The return_doc does not match! Expected: {expected_return}, but got: {return_doc}"
    assert notes_doc == expected_note, f"Error: The notes_doc does not match! Expected: {expected_note}, but got: {notes_doc}"

def test_extract_brief_and_tags_single_line():
    body_lines = [
        "@brief One-liner",
        "@param foo just foo",
        "@return success",
        "@note NotingThings"
    ]

    brief, param_docs, return_doc, notes_doc, _, _ = extract_brief_and_tags(body_lines)

    assert brief == "One-liner"
    assert param_docs == {"foo": "just foo"}
    assert return_doc == "success"
    assert notes_doc == "NotingThings"

def test_extract_brief_and_tags_missing_tags():
    body_lines = [
        "This is just a random comment line",
        "without any tags or formatting"
    ]

    brief, param_docs, return_doc, notes_doc, _, _ = extract_brief_and_tags(body_lines)

    assert brief == ""
    assert param_docs == {}
    assert return_doc == ""
    assert notes_doc == ""

def test_extract_brief_and_tags_pointer_input():
    body_lines = [
        "@brief picOpen() Callback Function to Open a Picture-File for Read",
        "e.g. for .png or .gif file Open",
        "@param *filename Containing whole path to the file incl. directory informations",
        "@param *size file size [Bytes]"
    ]

    brief, param_docs, _, _, _, _ = extract_brief_and_tags(body_lines)

    assert brief == "picOpen() Callback Function to Open a Picture-File for Read\n *        e.g. for .png or .gif file Open"
    assert param_docs == {"*filename": "Containing whole path to the file incl. directory informations",
                          "*size": "file size [Bytes]"}

def test_other_varaints_and_other_tags():
    body_lines = [
        "@brief Doing some HeaderBrief-Blabla",
        "@brief Multibrief",
        "@returns Nonesense if it is nonsense",
        "@returns Sense, if it makes sense",
        "@note wear sunglasses!",
        "@see Watch out while looking in the sun without sunglasses",
        "@description This is a description that should not be used",
        "@brief anotherBrief"
    ]

    brief, param_docs, return_doc, notes_doc, tparam_docs, other_docs = extract_brief_and_tags(body_lines)

    assert brief == "Doing some HeaderBrief-Blabla\n *        Multibrief\n *        anotherBrief"
    assert return_doc == "Nonesense if it is nonsense\n *         Sense, if it makes sense"
    assert notes_doc == "wear sunglasses!"
    assert param_docs == {}
    assert tparam_docs == {}
    assert other_docs == {
        "see": ["Watch out while looking in the sun without sunglasses"],
        "description": ["This is a description that should not be used"]
        }
