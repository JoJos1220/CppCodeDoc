# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import re

def extract_brief_and_tags(body_lines):
    brief_lines, return_lines, notes_lines = [], [], []
    current_tag, current_param, current_tparam = None, None, None
    param_docs, tparam_docs, other_tags = {}, {}, {}

    for line in body_lines:
        line = line.strip()

        # Detection of Doxygen @brief - TAG
        if line.startswith("@brief"):
            content = line[len("@brief"):].strip()
            brief_lines.append(content)
            current_tag = "brief"
        # Detection of Doxygen @param - TAG
        elif line.startswith("@param"):
            match = re.match(r"@param\s+([*&]?\w+)\s*(.*)", line)
            if match:
                current_param, desc = match.groups()
                param_docs[current_param] = [desc.strip()] if desc else []
                current_tag = "param"
            else:
                current_tag = None

        # Detection of Doxygen @tparam - TAG
        elif line.startswith("@tparam"):
            match = re.match(r"@tparam\s+(\w+)\s*(.*)", line)
            if match:
                current_tparam, desc = match.groups()
                tparam_docs[current_tparam] = [desc.strip()] if desc else []
                current_tag = "tparam"
            else:
                current_tag = None

        # Detection of Doxygen @return - TAG
        elif line.startswith("@return") or line.startswith("@returns"):
            line = line.replace("@returns", "@return", 1)
            content = line[len("@return"):].strip()
            if content:
                return_lines.append(content)
            current_tag = "return"
        # Detection of Doxygen @note - TAG
        elif line.startswith("@note"):
            content = line[len("@note"):].strip()
            notes_lines.append([content] if content else [])
            current_tag = "note"
        # Detection of Doxygen ALL OTHER - TAGs
        elif line.startswith("@"):
            # other Tags are ignored
            tag_match = re.match(r"@(\w+)\s*(.*)", line)
            if tag_match:
                tag, content = tag_match.groups()
                if tag not in ("brief", "param", "tparam", "return", "note"):
                    other_tags.setdefault(tag, []).append(content.strip())
                    current_tag = f"other:{tag}"
                else:
                    current_tag = None
            else:
                current_tag = None
        else:
            # Ongoing of the descriptoion
            if current_tag == "brief":
                brief_lines.append(line)
            elif current_tag == "param" and current_param:
                param_docs[current_param].append(line)
            elif current_tag == "tparam" and current_tparam:
                tparam_docs[current_tparam].append(line)
            elif current_tag == "return":
                return_lines.append(line)
            elif current_tag == "note" and notes_lines:
                notes_lines[-1].append(line.strip())
            elif current_tag and current_tag.startswith("other:"):
                tag = current_tag.split(":", 1)[1]
                other_tags[tag].append(line)

   # formating of @brief, @param and @return
    brief_text = "\n".join(f" *        {line.strip()}" if i > 0 else line.strip() for i, line in enumerate(brief_lines)).strip()

    # @param documentation – if multiline parameter descriptions are present
    param_docs = {
        name: "\n".join(f" *        {line.strip()}" if i > 0 else line.strip() for i, line in enumerate(lines)).strip()
        for name, lines in param_docs.items()
    }

    # @tparam documentation – multiline support
    tparam_docs = {
        name: "\n".join(f" *        {line.strip()}" if i > 0 else line.strip() for i, line in enumerate(lines)).strip()
        for name, lines in tparam_docs.items()
    }

    # @return documentation – if multiline return descriptions are present
    return_doc = "\n".join(
        f" *         {line.strip()}" if i > 0 else line.strip()
        for i, line in enumerate(return_lines)
        ).strip()

    notes_text = "\n".join(
        "\n".join(f" *        {line.strip()}" if i > 0 else line.strip() for i, line in enumerate(note)).strip()
        for note in notes_lines
    )

    return brief_text, param_docs, return_doc, notes_text, tparam_docs, other_tags

def split_function_params(param_str):
    """
    Splits function parameters, avoiding splits inside nested parentheses, angle brackets, and square brackets.
    """
    params = []
    current = ""
    depth_angle, depth_round, depth_square = 0, 0, 0

    for char in param_str:
        if char == '<':
            depth_angle += 1
        elif char == '>':
            depth_angle -= 1
        elif char == '(':
            depth_round += 1
        elif char == ')':
            depth_round -= 1
        elif char == '[':
            depth_square += 1
        elif char == ']':
            depth_square -= 1
        elif char == ',' and depth_angle == 0 and depth_round == 0 and depth_square == 0:
            params.append(current.strip())
            current = ""
            continue
        current += char

    if current.strip():
        params.append(current.strip())
    return params

def extract_func_ptr_info(p):
    """
    Extrahiert den Namen des Funktionszeiger-Parameters sowie dessen interne Signatur.
    Gibt (param_name, internal_signature) zurück.
    """
    # Beispiel: void (*SSEhandleRequest)(AsyncWebServerRequest *request)
    match = re.match(r'(.*?)\(\*\s*(\w+)\s*\)\s*\((.*?)\)', p)
    if match:
        return match.group(2), match.group(3)  # param_name, internal_signature
    return None, None

def extract_param_name(p):
    """
    Extrahiert den Namen des Parameters, auch bei Zeigern und Referenzen.
    """
    # Entferne Default-Wert
    p_clean = p.split('=')[0].strip() if '=' in p else p.strip()

    # Fucntionpointer?
    param_name, _ = extract_func_ptr_info(p_clean)
    if param_name:
        return param_name

    # Jetzt robust: Suche letzten Wortteil (der Name) getrennt von *, &
    tokens = re.findall(r'[\w:]+|\*+|&+', p_clean)

    if not tokens:
        return ""

    # Iteriere rückwärts, bis ein gültiger Identifier gefunden wird
    for token in reversed(tokens):
        if re.match(r'^[A-Za-z_]\w*$', token):
            return token
    return ""

def clean_suffixes(text):
    text = re.sub(r'( – default value if not overloaded: [^\(]+)', '', text)
    text = re.sub(r'( \(internal function parameter: [^)]+\))', '', text)
    return text.rstrip()

def generate_doxygen_comment(func):
    param_lines, notes_text = [], []
    comment_text, return_doc = "", ""
    param_docs, tparam_docs, other_docs = {}, {}, {}

    comment = func.get("comment", "").strip()
    has_comment = bool(comment)
    is_doxygen = bool(func["isDoxygenComment"])

    if has_comment and is_doxygen:
        # Verarbeite bestehenden Doxygen-Kommentar
        lines = comment.splitlines()
        body_lines = []
        for line in lines[1:-1]:  # überspringe /** und */
            line = line.strip()
            line = re.sub(r'^\*+\s?', '', line)  # führende * entfernen
            body_lines.append(line)

        # Extrahiere brief und tags
        comment_text, param_docs, return_doc, notes_text, tparam_docs, other_docs = extract_brief_and_tags(body_lines)

        if not comment_text:
            comment_text = f"TODO {func['name']} description."

    elif has_comment and not is_doxygen:
        # Kommentar vorhanden, aber kein Doxygen: ganzen Text sinnvoll extrahieren
        lines = comment.splitlines()
        body_lines = []

        for line in lines:
            line = line.strip()
            # Entferne Sterne, Bindestriche, Slashes, Kommentar-Marker etc.
            line = re.sub(r'^[/\*\-\s]+', '', line)
            if line:
                body_lines.append(line)

        # Alles zu einem zusammenhängenden Text verbinden
        comment_text = "\n * ".join(body_lines) if body_lines else f"TODO {func['name']} description."
    else:
        # Kein Kommentar oder kein Doxygen-Format -> neuer Kommentar
        comment_text = f"TODO {func['name']} description."

    # Parameterdokumentation aufbauen
    for p in split_function_params(func["params"]):
        p = p.strip()

        if not p:
            continue

        # Default-Wert extrahieren (wenn vorhanden)
        default_value = None
        if '=' in p:
            param_def_split = p.split('=')
            p_no_default = param_def_split[0].strip()
            default_value = '='.join(param_def_split[1:]).strip()
        else:
            p_no_default = p

        # Parametername und ggf. interne Funktionssignatur extrahieren
        param_name = extract_param_name(p)
        _, internal_sig = extract_func_ptr_info(p_no_default)

        if param_name == "void":
            continue

        if param_name in param_docs:
            doc_line = f" * @param {param_name} {param_docs[param_name]}"
        else:
            doc_line = f" * @param {param_name} TODO"

        doc_line = clean_suffixes(doc_line)

        # Optionaler Hinweis auf Default-Wert
        if default_value:
            doc_line += f" – default value if not overloaded: {default_value}"

        # Optionaler Hinweis auf interne Parameter einer Funktionspointer-Signatur
        if internal_sig:
            doc_line += f" (internal function parameter: {internal_sig})"

        param_lines.append(doc_line)

    # Falls keine tparam-Dokumentation vorhanden ist, aber die Funktion ein Template ist
    if not tparam_docs and func.get("isTemplate") and func.get("templateParams"):
        tparams_raw = func["templateParams"]
        # Entferne umschließende < > falls vorhanden
        if tparams_raw.startswith("<") and tparams_raw.endswith(">"):
            tparams_raw = tparams_raw[1:-1].strip()

        for tparam in split_function_params(tparams_raw):
            tparam = tparam.strip()
            if not tparam:
                continue
            tparam_name = tparam.split()[-1]  # z. B. bei "typename T" -> "T"
            tparam_docs[tparam_name] = ["TODO"]

    # Template-Parameterdokumentation
    tparam_lines = []
    for tparam_name, doc_lines in tparam_docs.items():
        if isinstance(doc_lines, str):
            doc_lines = [doc_lines]

        doc_text = " ".join(line.strip() for line in doc_lines if line.strip())
        if not doc_text:
            doc_text = "TODO"
        tparam_line = f" * @tparam {tparam_name} {doc_text}"
        tparam_line = clean_suffixes(tparam_line)
        tparam_lines.append(tparam_line)

    # Rückgabewert
    return_text = ""
    if "void" not in func["return_type"] and func["return_type"] != "":
        if return_doc:
            return_text = f"\n * @return {return_doc}"
        else:
            return_text = "\n * @return TODO"
    else:
        return_text = ""

    tparam_block = "\n" + "\n".join(tparam_lines) if tparam_lines else ""
    param_block = "\n" + "\n".join(param_lines) if param_lines else ""

    notes_section = ""
    if notes_text:
        # Falls notes_text ein String ist, wandle ihn in eine Liste von Listen um
        if isinstance(notes_text, str):
            notes_text = [[notes_text]] if notes_text.strip() else []

        formatted_notes = []
        for note in notes_text:
            if not note:
                continue
            formatted = "\n".join(
                f" *        {line.strip()}" if i > 0 else f" * @note {line.strip()}"
                for i, line in enumerate(note)
            )
            formatted_notes.append(formatted)
        if formatted_notes:
            notes_section = "\n" + "\n".join(formatted_notes)

    other_section = ""
    for tag, entries in other_docs.items():
        if not entries:
            continue
        lines = []
        for i, entry in enumerate(entries):
            prefix = f" * @{tag} " if i == 0 else " *        "
            lines.append(prefix + entry.strip())
        other_section += "\n" + "\n".join(lines)

    func["doxygen"] = (
        "/**\n"
        f" * @brief {comment_text}"
        + tparam_block +
        param_block +
        return_text +
        notes_section +
        other_section +
        "\n */"
    )
