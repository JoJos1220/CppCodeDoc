# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import os
import re
import shutil
from pathlib import PurePath

def normalize_signature(sig: str) -> str:
    # Entfernt doppelte Leerzeichen und normalisiert Pointer-Abstände
    # Beginne mit dem Entfernen von Blockkommentaren
    sig = re.sub(r'/\*.*?\*/', '', sig)
    normalized = re.sub(r'\s+', ' ', sig.strip().replace(' *', '*').replace(' &', '&'))
    normalized = re.sub(r'\s*=\s*', '=', normalized)  # normalization of equal signs
    print(f"[code_parser][normalize_signature] Input: '{sig}' -> Output: '{normalized}'")
    return normalized

def extract_param_signature(buffer: str) -> str:
    print(f"[code_parser][extract_param_signature] Raw buffer: '{buffer}'")
    start = buffer.find('(')
    if start == -1:
        print("[code_parser][extract_param_signature] No opening parenthesis found.")
        return ""

    depth = 0
    for i in range(start, len(buffer)):
        if buffer[i] == '(':
            depth += 1
        elif buffer[i] == ')':
            depth -= 1
            if depth == 0:
                param_block = buffer[start + 1:i]
                # Cleaning up inline comments and block comments
                return normalize_signature(param_block)

    print("[code_parser][extract_param_signature] No matching closing parenthesis found.")
    return ""

def find_function_start_line(content: str, function_name: str, param_signature: str = None, occurrence: int = 1) -> int:
    print(f"[code_parser][find_function_start_line]\n=== search for function'{function_name}' with parameter '{param_signature}' ===")
    match_count = 0
    lines = content.splitlines()
    if function_name.startswith("operator"):
        # Operator-name, but no alphanumeric characters should be escaped
        # Only escape special characters after "operator"
        base = "operator"
        suffix = function_name[len(base):]
        # only escape special characters in the suffix
        escaped_suffix = re.escape(suffix)
        escaped_name = base + escaped_suffix
    else:
        escaped_name = re.escape(function_name)
        escaped_name = escaped_name.replace("\\~", "~")
    param_signature = normalize_signature(param_signature) if param_signature is not None else None

    start_index = None
    buffer = ""
    in_block_comment = False

    for idx, line in enumerate(lines):
        stripped = line.strip()

        # Ingoring comments
        if stripped.startswith("/*"):
            if "*/" in stripped:
                continue
            in_block_comment = True
            continue
        if in_block_comment:
            if "*/" in stripped:
                in_block_comment = False
            continue
        if stripped.startswith("//"):
            continue

        # Check for function definition
        if start_index is None:
            # Checking for Constructor/Destructor or function definition (NO FUNCTION CALLS)
            if re.search(rf'{escaped_name}\s*\(', stripped):
                print("[code_parser][find_function_start_line] → function definition found!")
                is_definition = bool(re.match(
                    rf'^\s*(?:[\w:\s<>\[\],*&]+)?\s*{escaped_name}\s*\(',
                    stripped
                ))

                # Checking for one-liner-Destructor/Constructor definition
                is_destructor = bool(re.match(
                    rf'^\s*{escaped_name}\s*\(\s*\)\s*\{{.*\}}\s*;',
                    stripped
                ))

                is_call = re.match(rf'.*\b{escaped_name}\b\s*\(.*\)\s*;', stripped)
                
                if is_definition and not is_call:
                    print(f"\n[Line {idx}] {line.strip()}")
                    print("  → Potentieller Funktionsstart gefunden")
                    start_index = idx
                    buffer = stripped
                    
                    # Applying to the destructor or constructor
                    if is_destructor:
                        print("  [DEBUG] Destruktor erkannt.")
                        actual_params = extract_param_signature(buffer)
                        print(f"  [DEBUG] actual_params = '{actual_params}'")
                        print(f"  [DEBUG] expected      = '{param_signature}'")
                        if param_signature is None or normalize_signature(actual_params).lower() == normalize_signature(param_signature).lower():
                            match_count += 1
                            if match_count == occurrence:
                                print("  ✅ Match found (Destructor found)")
                                return start_index
                            else:
                                print("  ➕ Matching function start, but not correct function order.")
                                start_index = None
                                buffer = ""
                    
                    # Constructor or other function
                    if "{" in stripped:
                        actual_params = extract_param_signature(buffer)
                        print(f"  [DEBUG] actual_params = '{actual_params}'")
                        print(f"  [DEBUG] expected      = '{param_signature}'")
                        if param_signature is None or normalize_signature(actual_params).lower() == normalize_signature(param_signature).lower():
                            match_count += 1
                            if match_count == occurrence:
                                print("  ✅ Match found (inline)")
                                return start_index
                            else:
                                print("  ➕ Matching function start, but not correct function order.")
                                start_index = None
                                buffer = ""
                        else:
                            print("  ❌ No Match, reset")
                            start_index = None
                            buffer = ""
        else:
            buffer += " " + stripped
            if "{" in stripped:
                print(f"\n[Line {idx}] {line.strip()}")
                print("  → End of Functiondeclaration (multiline)")
                actual_params = extract_param_signature(buffer)
                print(f"  [DEBUG] actual_params = '{actual_params}'")
                print(f"  [DEBUG] expected      = '{param_signature}'")
                if not param_signature or normalize_signature(actual_params).lower() == normalize_signature(param_signature).lower():
                    match_count += 1
                    if match_count == occurrence:
                        print("  ✅ Match found (multiline)")
                        return start_index
                    else:
                        print("  ➕ Matching function start, but not correct function order.")
                        start_index = None
                        buffer = ""
                else:
                    print("  ❌ No Match, reset")
                    start_index = None
                    buffer = ""

    print("🔚 Function not found.")
    return -1

def remove_strings_and_comments(lines):
    in_block_comment = False
    result = []

    # Total Regex for Literale
    string_regex = re.compile(r'"(\\.|[^"\\])*"')
    char_regex = re.compile(r"'(\\.|[^'\\])'")

    for line in lines:
        if not in_block_comment:
            line = string_regex.sub('""', line)
            line = char_regex.sub("''", line)

        new_line = []
        i = 0
        while i < len(line):
            if in_block_comment:
                if line[i:i+2] == "*/":
                    in_block_comment = False
                    i += 2
                else:
                    i += 1
            else:
                if line[i:i+2] == "/*":
                    in_block_comment = True
                    i += 2
                elif line[i:i+2] == "//":
                    break
                else:
                    new_line.append(line[i])
                    i += 1
        result.append("".join(new_line))
    return result

def find_function_end_line(lines, start_line):
    """
    Seaching for the end of a function starting at start_line.
    During that, opening and closing curly braces are counted.
    Retuns: The line number (including start_line) of the closing curly brace.
    """
    brace_count = 0
    cleaned_lines = remove_strings_and_comments(lines)

    for i in range(start_line, len(cleaned_lines)):
        code = cleaned_lines[i]
        brace_count += code.count("{")
        brace_count -= code.count("}")
        if brace_count == 0 and "}" in code:
            return i
        
    return None

def mask_templates(line: str):
    stack, templates = [], []
    masked = ''
    i, last_pos, placeholder_count = 0, 0, 0

    while i < len(line):
        if line[i] == '<':
            if not stack:
                last_pos = i
            stack.append(i)
        elif line[i] == '>' and stack:
            stack.pop()
            if not stack:
                # total template-block
                original = line[last_pos:i+1]
                placeholder = f"__TPL{placeholder_count}__"
                templates.append((placeholder, original))
                masked += line[:last_pos] + placeholder
                line = line[i+1:]
                i = -1
                placeholder_count += 1
        i += 1

    masked += line
    return masked, dict(templates)

def extract_multiline_comments(lines):
    """
    Collecting block comments that are in their own lines, and return them as a list of tuples.
    """
    comments = []
    comment_start = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("/*") and comment_start is None:
            comment_start = i
        if comment_start is not None and stripped.endswith("*/"):
            comment_text = "\n".join(lines[comment_start:i+1])
            comments.append((comment_start, i, comment_text))
            comment_start = None
            
    return comments

def join_multiline_function_declarations(lines):
    """
    Collecting multi-line function declarations and joining them into a single line.
    Returns:
        final_lines: list[str]          → zusammengesetzte, ggf. gesplittete Funktionszeilen
        final_mapping: list[int]        → für jede final_line die Original-Zeile (letzte relevante)
        startline_map: list[int]        → für jede final_line die ursprüngliche Startzeile der Funktion
    """
    joined, mapping, starts = [], [], []
    i = 0
    while i < len(lines):
        raw = lines[i].strip()

        # Take directly, if empty line, only comment or visibility modifier
        if not raw or raw.startswith(("//", "/*", "*", "*/")) or raw in ("public:", "private:", "protected:"):
            joined.append(lines[i])
            mapping.append(i)
            starts.append(i)
            i += 1
            continue

        if '(' in raw and '{' in raw and raw.endswith('}') and raw.count('{') == 1 and raw.count('}') == 1:
            joined.append(lines[i])
            mapping.append(i)
            starts.append(i)
            i += 1
            continue

        # Special case: multiple functions in one line → split later
        if ('(' in raw and '{' in raw and raw.endswith('}')
            and (raw.count('{') > 1 or raw.count('}') > 1)):
            joined.append(lines[i])
            mapping.append(i)
            starts.append(i)
            i += 1
            continue

        if '(' in raw and not raw.endswith(';') and not raw.startswith('#'):
            cur = raw
            paren_level = raw.count('(') - raw.count(')')
            start = i

            while (paren_level > 0 or not cur.rstrip().endswith('{')) and i + 1 < len(lines):
                nxt = lines[i + 1].strip()

                if not nxt or nxt.startswith(("//", "/*", "*", "#")):
                    break

                if nxt.startswith('{'):
                    comment_match = re.search(r'//|/\*', cur)
                    if comment_match:
                        cur = cur[:comment_match.start()].rstrip()
                        
                i += 1
                cur += ' ' + nxt
                paren_level += nxt.count('(') - nxt.count(')')

                if cur.rstrip().endswith(('{', ';')):
                    break

            joined.append(cur)
            mapping.append(i)
            starts.append(start)
            i += 1
        else:
            joined.append(lines[i])
            mapping.append(i)
            starts.append(i)
            i += 1

    # Splitting multi-line function declarations into individual lines
    split_lines, split_mapping, split_startlines = [], [], []

    for line, idx, start in zip(joined, mapping, starts):
        # delete commments to prevent splitting issues
        line_clean = re.sub(r'/\*.*?\*/', '', line).strip()

        # splitting only if there is a '}' + optional comment + new function head
        parts = re.split(
            r'}\s*(?=(?:/\*.*?\*/\s*)*[\w:~]+\s+[\w:~]+\s*\()',  # match "int sub(", "void foo(", etc.
            line_clean
        )
        # filling the split parts with the closing brace, only if it is not the last part
        for j, part in enumerate(parts):
            if j < len(parts) - 1:
                part += '}'
            part = part.strip()
            if part:
                split_lines.append(part)
                split_mapping.append(idx)
                split_startlines.append(start)

    final_lines, final_mapping, final_startlines = [], [], []

    for line, idx, start in zip(split_lines, split_mapping, split_startlines):
        # delete comments to prevent splitting issues
        line_clean = re.sub(r'/\*.*?\*/', '', line).strip()

        # always split if there is a '}' + '{' + return in the line
        if line_clean.count('{') == 1 and line_clean.count('}') == 1:
            head, body = line.split('{', 1)
            body = body.strip()
            if body.endswith('}'):
                body_content = body[:-1].strip()

                # check if body_content is empty or contains 'return' or ';'
                if (not body_content) or ('return' in body_content) or (';' in body_content):
                    final_lines.append(f"{head.strip()} {{")
                    final_mapping.append(idx)
                    final_startlines.append(start)
                    final_lines.append(f"{body_content} }}")
                    final_mapping.append(idx)
                    final_startlines.append(start)
                    continue

        final_lines.append(line)
        final_mapping.append(idx)
        final_startlines.append(start)

    return final_lines, final_mapping, final_startlines


def extract_comment_for_function(lines, orig_idx, multiline_comments):
    """
    Extracts the comment directly above the function at orig_idx.
    """
    # Check for Multiline-Blockcomments
    comment = ''
    for start, end, ctext in reversed(multiline_comments):
        if end < orig_idx and all(lines[j].strip().startswith('/*') or lines[j].strip().startswith('*') for j in range(start, end+1)):
            # sicherstellen, dass Kommentarblock ist und direkt über Funktion
            if all(not lines[j].strip() or lines[j].lstrip().startswith('#') for j in range(end+1, orig_idx)):
                comment = ctext
            break

    # Check for Signle-Line-Blockcomments
    if not comment:
        # If ther is no /* */ comment: // gathering lines
        collected = []
        j = orig_idx - 1
        while j >= 0:
            stripped = lines[j].strip()
            if not stripped:
                # If there is an empty line -> BREAK
                break
            if stripped.startswith('#'):
                j -= 1
                continue
            if stripped.startswith('//'):
                collected.append(stripped)
                j -= 1
            else:
                # Somthing else then // found -> BREAK
                break
        if collected:
            collected.reverse()
            comment = "\n".join(collected)
    return comment

def is_in_comment_block(line_idx, comments):
    for start, end, _ in comments:
        if start <= line_idx <= end:
            return True
    return False

def sync_multiline_comments_to_joined_lines(multiline_comments, original_lines_count, final_startlines):
    """
    Sync block comment start/end indices from original lines to indices in joined lines
    - multiline_comments: List of (start, end, text) with original line indices
    - original_lines_count: Anzahl der originalen Lines (int)
    - final_startlines: List[int], für jede joined line die ursprüngliche Startzeile
    
    Return:
        synced_comments: List of (start_idx_in_joined, end_idx_in_joined, text)
    """
    synced_comments = []

    # for each comment, we check which index in final_startlines fits it.
    # A comment can span multiple lines, it is sufficient to map the start index.    
    for c_start, c_end, c_text in multiline_comments:
        # Seaching for the start and end index in final_startlines
        # final_startlines is a list of start lines for each joined line.
  
        start_idx_in_joined = None
        end_idx_in_joined = None
        
        for i in range(len(final_startlines)):
            start_line = final_startlines[i]
            next_start_line = final_startlines[i+1] if i+1 < len(final_startlines) else original_lines_count
            
            if start_line <= c_start < next_start_line:
                start_idx_in_joined = i
            if start_line <= c_end < next_start_line:
                end_idx_in_joined = i
                
            # If both is found, abort
            if start_idx_in_joined is not None and end_idx_in_joined is not None:
                break
        
        # if not found, we try to find the closest match
        if start_idx_in_joined is None:
            start_idx_in_joined = 0
        if end_idx_in_joined is None:
            end_idx_in_joined = start_idx_in_joined
        
        synced_comments.append((start_idx_in_joined, end_idx_in_joined, c_text))
    
    return synced_comments

def extract_functions_from_string(content: str, file_path: str = "<memory>"):
    """
    Extracting functions from the given content string.
    For each function we determine:
    - The function name
    - The return type
    - The parameter list as a string
    - Whether the function is marked as "const"
    - A comment block directly above the function (if available, only multi-line comments)
    - Whether the comment is a Doxygen-style comment
    - The file name (or path) where the function is defined
    ignores Control-Statements like if, else, for, while, switch, case and template lines.
    """
    lines = content.splitlines()
    functions = []

    # Gathering Blockcomments in single-lines
    multiline_comments = extract_multiline_comments(lines)

    # Gatehring multiline function declarations together
    joined_lines, _, final_startlines = join_multiline_function_declarations(lines)

    # syncing multiline_comments to joined_lines Index and popping out single-liner
    synced_multiline_comments = sync_multiline_comments_to_joined_lines(multiline_comments, len(lines), final_startlines)

    for idx, (start, end, text) in reversed(list(enumerate(synced_multiline_comments))):
        if start == end:
            synced_multiline_comments.pop(idx)

    # General Function detection pattern
    pattern = re.compile(r"""
        ^\s*
        (?P<rtype>\w[\w\s:*&<>]*?)\s*                                       # return type
        (?P<name>(\w+::)*[\w~]+|operator\s*[\w\[\]\(\)\+\-\*/<>=!&|^%~]+)
        \s*\(
        (?P<params>[^()]*(?:\([^)]*\)[^()]*)*)
        \)                                                                  # parameter list (1-level nested)
        \s*(?P<const>const)?                                                # optional const       
        \s*(\{)?\s*$                                                        # optional '{' at the end or in next line
        """, re.VERBOSE)
    
    # Constructor/Destructor detection pattern
    ctor_pattern = re.compile(r"""
        ^\s*(?P<name>(\w+::)?~?\w+)\s*              # Const-/Destructor name
        \((?P<params>[^)]*)\)\s*                    # Parameter
        (?:\s*:\s*(?P<initlist>[^{}]*))?            # opt.: Initialisation list
        (?P<const>const)?\s*                        # opt.: const
        \{                                          # Opening Braces
        """, re.VERBOSE)

    control_keywords = ('if', 'else', 'for', 'while', 'switch', 'case')

    template_line, template_params = None, None

    for idx, line in enumerate(joined_lines):
        # First check, if Parser is within multiline comment and skip this line
        if is_in_comment_block(idx, synced_multiline_comments):
            continue
        
        # masking complex functionpattern and saving
        # the original template for later use
        # first mask complex patterns
        masked_line, tpl_map = mask_templates(line)

        # skip templates  
        if masked_line.startswith('template'):
            template_line = masked_line.strip()
            match_tpl = re.match(r'^template\s+(__TPL\d+__)', template_line)
            if match_tpl:
                template_params = match_tpl.group(1).strip()
                # demasking Function pattern back to original template
                for key, val in tpl_map.items():
                    if template_params:
                        template_params = template_params.replace(key, val)
                # if template was found, extract definition to avoid retval containing "template __TPxxx__"
                masked_line = re.sub(r'\btemplate\s+__TPL\d+__\s*', '', masked_line)
            else:
                template_params = None

        # skip control statements
        if re.match(rf"^\s*(?:{'|'.join(control_keywords)})\b", masked_line):
            continue
        
        # Delete singelton blockkoments and inline-comments (/* ... */) (// ...)
        masked_line = re.sub(r'/\*.*?\*/', '', masked_line)
        masked_line = re.sub(r'//.*$', '', masked_line).rstrip()

        ctor_match = ctor_pattern.match(masked_line)
        match = None
        if not ctor_match:
            match = pattern.match(masked_line)

        if not match and not ctor_match:
            continue
        
        if match and not masked_line.strip().endswith('{'):
            # checking in originallines, if the next line has a '{'
            next_line_idx = idx + 1
            while next_line_idx < len(joined_lines):
                next_line = re.sub(r'/\*.*?\*/', '', joined_lines[next_line_idx]).strip()
                if next_line.startswith('{'):
                    break  # valid function call
                elif not next_line or next_line.startswith('//') or next_line.startswith('/*'):
                    next_line_idx += 1  # empty line, or ignore comment
                else:
                    match = None  # no vaild function head found
                    break

        if match:
            rtype = match.group('rtype').strip()
            name = match.group('name')
            params = match.group('params').strip()
            constness = bool(match.group('const'))
        else:
            rtype = ''
            name = ctor_match.group('name')
            params = ctor_match.group('params').strip()
            constness = bool(ctor_match.group('const'))

        # demasking Function pattern back to original template
        for key, val in tpl_map.items():
            rtype = rtype.replace(key, val)
            params = params.replace(key, val)

        orig_idx = final_startlines[idx]

        is_template = bool(template_line)
        final_template_params = template_params if is_template else None

        # seaching for comment directly above 
        # Checking for Multiline-blockcomments
        comment = extract_comment_for_function(lines, orig_idx, multiline_comments)

        # determine isDoxygenComment or not
        is_doxygen = comment.startswith('/**') or '@brief' in comment

        # Count up how often the function is defined (e.g. in #if/#else statements)
        count = 1
        for f in functions:
            if f['name'] == name and f['params'] == params:
                count += 1

        functions.append({
            'name': name,
            'return_type': rtype,
            'params': params,
            'const': constness,
            'comment': comment,
            'isDoxygenComment': is_doxygen,
            'file': file_path,
            'startLine': orig_idx,
            'count': count,
            "isTemplate": is_template,
            "templateParams": final_template_params
        })

        template_line = None
        template_params = None

    return functions

def extract_functions(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return extract_functions_from_string(content, file_path)

def header_comment_exists(lines, func_start):
    """
    Checks if a valid header comment exists directly above the function.
    A header comment is:
    - A block comment that starts with "/*" and ends with "*/"
    - a single-line comment that starts with "//"
    - Directly attached to the function (without a blank line in between)
    - At least 2 lines long
    - Not a footer comment, which might appear after a closing curly brace
    """

    if func_start == 0:
        return False

    # start with line above the function
    i = func_start - 1

    # if directly above the function is a empty line, return False
    if lines[i].strip() == "":
        return False

    # search for candidatte block for header comment until a empty line is found
    candidate = []
    while i >= 0:
        stripped = lines[i].strip()

        # if line is empty, break
        if stripped == "":
            break

        # if a "}" is found at the END, break - because this is NOT a header comment candidadte
        if stripped.endswith("}") or stripped.endswith("};") or stripped.endswith("}/*"):
            break

        # if a "}" is found at the BEGINNING, break - because this is NOT a header comment candidadte
        if stripped.startswith("}/*") or stripped.startswith("} /*") or stripped.startswith("}"):
            break
        
        candidate.insert(0, lines[i])
        i -= 1

    block = "\n".join(candidate)

    # Line hould not end with an "*/" and a "}" direct in previous,
    #  → Footer-Command-Candidate found
    if func_start >= 2 and lines[func_start - 2].strip().endswith("}"):
        return False

    # Muss mit Blockkommentar starten
    if block.strip().startswith("/*"):
        # MultiLine Header-Comment Block with /* */
        return True
    elif candidate and all(line.strip().startswith("//") for line in candidate):
        # Check Ok for "One-Lined" header-Comment Block consisting of multiline
        # "//"
        return True
    else:
        # Invalid Header-Comment Block    
        return False

def convert_single_line_comment_to_header(lines, func_start):
    """
    Converting an existing single-line comment block (//) directly above a function
    into a standard block comment (/* ... */).
    """
    if func_start == 0:
        return lines

    i = func_start - 1

    # ignoring empty lines
    while i >= 0 and lines[i].strip() == "":
        i -= 1

    if i < 0:
        return lines

    candidate = []
    while i >= 0 and lines[i].strip().startswith("//"):
        candidate.insert(0, lines[i].strip()[2:].strip())  # "//" deleting, Text extracting
        i -= 1

    if not candidate:
        return lines  # No Single-Line comments available

    # Deleting old single-line comments
    lines = lines[:i+1] + lines[func_start:]

    # Building new blockcomment
    header_block = [
        "/*-----------------------------------------------------------------------------",
    ]

    for line in candidate:
        if line:
            header_block.append(f" * {line}")
        else:
            header_block.append(" *")

    header_block.append(" * ----------------------------------------------------------------------------")
    header_block.append("*/")

    # Ensuring to empty lines
    pre_part = lines[:i+1]
    while pre_part and pre_part[-1].strip() == "":
        pre_part.pop()
    pre_part.extend(["", ""])

    # inserting new Header
    new_lines = pre_part + header_block + lines[i+1:]
    return new_lines

def add_header_comment(lines, func_name, start_line, comment_text=None):
    """
    Insert a header comment block before the function at start_line.
    Bevor and after the comment block should be exactly two empty lines.
    if there is already a valid header comment (checked with header_comment_exists()),
    nothing will be inserted.
    """
    if header_comment_exists(lines, start_line):
        return lines  # valid header already exists.
    
    # Deleting empty lines at the end of the block before the function
    pre_part = lines[:start_line]
    while pre_part and pre_part[-1].strip() == "":
        pre_part.pop()
    # Inserting two empty lines
    pre_part.extend(["", ""])
    
    if comment_text is None:
        comment_text = f"{func_name} -->> TODO: Add your description here"
    elif isinstance(comment_text, list):
        # if comment_text is a list, convert it to a single string
        comment_text = " ".join(comment_text)

    # splitting up comment into lines
    comment_lines = comment_text.splitlines()

    # Block comment with starting "/*"
    header_block = [
        "/*-----------------------------------------------------------------------------"
    ]
    
    for line in comment_lines:
        header_block.append(f" * {line}")
    
    header_block.append(" * ----------------------------------------------------------------------------")
    header_block.append("*/")
    
    new_part = pre_part + header_block
    # inserting new header directly before the function
    new_lines = new_part + lines[start_line:]
    return new_lines

def is_inside_multiline_comment(lines, line_index):
    """
    Checking, if the given line is part of a multiline comment.
    Searching backwarts to the beginning of the file for an unparsed /* without */ 
    """
    up_to_line = "\n".join(lines[:line_index + 1])
    open_blocks = up_to_line.count("/*")
    close_blocks = up_to_line.count("*/")
    return open_blocks > close_blocks

def add_post_comment(lines, func_name, func_start_line):
    """
    Adding at the end of the function a Post-comment without empty line, basesd on func_start_line.
    Existing Inline-comments will be deleted within this line.
    """
    end_line = find_function_end_line(lines, func_start_line)
    if end_line is None:
        return lines

    original_line = lines[end_line].rstrip()

    # 1. checking against multiline-comment block
    if is_inside_multiline_comment(lines, end_line):
        return lines

    # 2. Checking for // comment
    match = re.match(r'^(.*?)(//\s*)(.*)$', original_line)
    if match:
        code_part = match.group(1).rstrip()
        comment_text = match.group(3).strip()
        lines[end_line] = f"{code_part} /* {comment_text} */"
        return lines

    # 3. checking for /* */ Comment
    if re.search(r'/\*.*\*/', original_line):
        return lines

    # 4. No comment → appending new one
    lines[end_line] = original_line + f" /* {func_name}() */"
    return lines

def make_file_backup(file_path, backup_base_path):
    """
    Creating Backup of the file im destination backup-folder.
    If folder does not exist, a new one is created
    """
    if (check_input_string_looks_like_path(backup_base_path)):
        if not os.path.exists(backup_base_path):
            os.makedirs(backup_base_path)
    else:
        print("Backup path has invalid Format!")
        return False

    filename = os.path.basename(file_path)
    backup_path = os.path.join(backup_base_path, filename + ".bak")
    shutil.copyfile(file_path, backup_path)
    print(f"🔄 Backup created: {backup_path}")
    return True

def check_input_string_looks_like_path(path_str: str) -> bool:
    if not isinstance(path_str, str) or len(path_str.strip()) < 3:
        return False

    path = PurePath(path_str.strip())

    # Prüfen, ob der letzte Pfadteil KEINE Dateiendung hat
    last_part = path.name
    if '.' in last_part and not last_part.startswith('.'):
        return False

    # Muss mehrteilig sein (z. B. nicht einfach "backup" oder "file.txt")
    if len(path.parts) < 2 and not path_str.startswith("./") and not path.is_absolute():
        return False

    return True

def convert_doxygen_to_default_comment(doxygen_comment):
    """
    Konvertiert einen Doxygen-Kommentar (mit @brief) in ein normales Block-Kommentar.
    """
    # Entfernen der Zeilenumbrüche und Leerzeichen vor und nach dem Kommentar
    doxygen_comment = doxygen_comment.strip()

    # Suche nach dem @brief-Tag und lese den gesamten Text bis zum nächsten Tag oder dem Ende des Kommentars
    match = re.search(r"\* @brief (.*?)(?=\* @\w+| \*/)", doxygen_comment, re.DOTALL)
    
    if match:
        comment_text = match.group(1).strip()

        # Entfernen von führendem " * " aus jeder Zeile
        comment_lines = comment_text.split('\n')
        comment_lines = [line.lstrip(" *").strip() for line in comment_lines]
        comment_text = '\n'.join(comment_lines)
        
    else:
        comment_text = "No description provided."
    
    # Füge den extrahierten Kommentar in das Standard-Format ein
    default_comment = [
        f"{comment_text}"
    ]
    
    return default_comment

def insert_comments(file_path, arguments):
    """
    Liest die Datei und verarbeitet alle Funktionen:
      - Für Funktionen ohne bestehenden Header-Kommentar wird ein Pre-Comment eingefügt,
        wobei vor dem Kommentar exakt 2 Leerzeilen stehen.
      - Zusätzlich wird, sofern eine vorherige Funktion existiert, an deren Endzeile
        (direkt nach der schließenden "}") ein Post-Comment angefügt.
      - Existiert bereits ein Header-Kommentar (und dieser wird nicht fälschlicherweise als Footer erkannt),
        wird der Einfügevorgang übersprungen.
    """
    functions = extract_functions(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
    
    # Bearbeite Funktionen von unten nach oben, damit sich Einfügungen nicht auf die Zeilenindizes auswirken.
    for idx in range(len(functions)-1, -1, -1):
        func = functions[idx]
        content = "\n".join(lines)
        start_line = find_function_start_line(content, func["name"], func["params"], func["count"])
        if start_line == -1:
            continue  # Funktion nicht gefunden
        
        if not func["comment"].strip() or not header_comment_exists(lines, start_line):
            # Falls noch kein Header vorhanden ist, füge ihn ein.
            lines = add_header_comment(lines, func["name"], start_line)
        elif func["comment"].strip() and func["isDoxygenComment"] == True and arguments["headerCommentStyle"] != "doxygen":
            # Convert Pre-Existing doxygen Style Command back to defaultHeader-Comment
            print(f"ℹ️ Converting Doxygen-style comment for {func['name']}")
            comment_text = convert_doxygen_to_default_comment(func["comment"])

            lines = remove_existing_header(lines, start_line)
            content = "\n".join(lines)
            start_line = find_function_start_line(content, func["name"], func["params"], func["count"])

            # Füge den Standard-Kommentar mit dem extrahierten Text ein
            lines = add_header_comment(lines, func["name"], start_line, comment_text)
        else:
            # Wenn nur Single-Line-Kommentar existiert, umwandeln
            i = start_line - 1
            while i >= 0 and lines[i].strip() == "":
                i -= 1
            if i >= 0 and lines[i].strip().startswith("//"):
                print(f"ℹ️ Converting single-line header comment for {func['name']}")
                lines = convert_single_line_comment_to_header(lines, start_line)
            else:
                print(f"ℹ️ for {func['name']} already exists an valid block-header-comment! No changes.")

    # Nun hänge die Post-Kommentare an – in natürlicher Reihenfolge.
    for func in functions:
        func_name = func["name"]
        func_params = func["params"]
        func_count = func["count"]
        content = "\n".join(lines)
        start_line = find_function_start_line(content, func_name, func_params, func_count)
        if start_line != -1:
            lines = add_post_comment(lines, func_name, start_line)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")
    
    print("✅ Header and Post Comments successfully evaluated.")

def replace_comments(file_path, functions):
    """
    Ersetzt vorhandene Doxygen-Header durch vorbereitete `func["doxygen"]`-Kommentare.
    Falls kein Kommentar existiert, wird er eingefügt (mit 2 Leerzeilen Abstand).
    """

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    for idx in range(len(functions)-1, -1, -1):
        func = functions[idx]
        content = "\n".join(lines)
        start_line = find_function_start_line(content, func["name"], func["params"], func["count"])
        if start_line == -1:
            continue  # Funktion nicht gefunden

        # Lösche bestehenden Header-Kommentar, falls vorhanden
        if header_comment_exists(lines, start_line):
            lines = remove_existing_header(lines, start_line)
            content = "\n".join(lines)
            start_line = find_function_start_line(content, func["name"], func["params"], func["count"])

        # Füge neuen Kommentar ein
        comment_lines = func["doxygen"].splitlines()
        insert_pos = start_line
        # Zwei Leerzeilen davor einfügen (aber nur, wenn da nicht schon Leerzeilen sind)
        while insert_pos > 0 and lines[insert_pos - 1].strip() == "":
            insert_pos -= 1

        # Sicherstellen, dass vor dem Kommentar zwei Leerzeilen eingefügt werden, falls notwendig
        if insert_pos >= 2 and lines[insert_pos - 2].strip() != "":
            comment_lines = [""] * 2 + comment_lines  # Zwei Leerzeilen VOR dem Kommentar einfügen
        elif insert_pos >= 1 and lines[insert_pos - 1].strip() != "":
            comment_lines = [""] + comment_lines  # Eine Leerzeile VOR dem Kommentar einfügen

        # Jetzt fügen wir den Kommentar vor der Funktion ein
        lines = lines[:insert_pos] + comment_lines + lines[insert_pos:]

        # Nach dem Kommentar nach Leerzeilen suchen und diese entfernen
        insert_pos_bevor = insert_pos + len(comment_lines)
        insert_pos_after = insert_pos_bevor
        while insert_pos_after < len(lines) and lines[insert_pos_after].strip() == "":
            insert_pos_after += 1

        # Entferne die Leerzeilen nach dem Kommentar
        lines = lines[:insert_pos_bevor] + lines[insert_pos_after:]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")

    # UND JETZT: Start-Linien neu bestimmen!
    content = "\n".join(lines)
    for func in functions:
        new_start = find_function_start_line(content, func["name"], func["params"], func["count"]) + 1
        func['startLine'] = new_start
        print(f"🔄 Funktion '{func['name']}' neue Startlinie: {new_start}")

    print("✅ Alle Header-Kommentare erfolgreich ersetzt oder eingefügt.")

def remove_existing_header(lines, func_start_line):
    """
    Entfernt den Header-Kommentar vor der Funktion.
    Die Funktion überprüft, ob ein Kommentarblock vorhanden ist und entfernt diesen.
    """
    idx = func_start_line - 1  # Wir gehen eine Zeile vor die Funktion

    # 1. Suchen nach dem Kommentaranfang (/*)
    while idx >= 0 and "/*" not in lines[idx]:
        idx -= 1  # weiter zurück gehen

    if idx < 0:
        return lines  # kein Kommentarblock gefunden

    # Kommentaranfang gefunden
    comment_start = idx

    # 2. Jetzt suchen nach dem Kommentarende (*/)
    idx += 1
    while idx < len(lines) and "*/" not in lines[idx]:
        idx += 1  # weiter nach unten gehen

    if idx >= len(lines):
        return lines  # kein Kommentar-Ende gefunden

    # Kommentar-Ende gefunden, alles dazwischen entfernen
    comment_end = idx

    # Die Zeilen ohne Kommentar zurückgeben
    return lines[:comment_start] + lines[comment_end + 1:]