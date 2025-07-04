# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

"""
Generating markdown documentation report out of functions.
"""

import os

def write_markdown_doc(functions, output_path, arguments, todo_stats):
    """
    writing documentation in markdown format
    """
    document_meta = arguments["document"]
    highlight_todo = document_meta.get("highlightTodo", False)
    show_progress = document_meta.get("showDocProgress", True)

    def format_doxygen_comment(comment: str) -> str:
        lines = comment.strip().split("\n")
        formatted, tag_buffer = [], []
        current_tag = None

        def flush_tag():
            nonlocal current_tag, tag_buffer
            if not current_tag:
                return
            content = " ".join(tag_buffer).strip()
            if current_tag == "@brief":
                formatted.append(f"**🔹 Description:** {content}")
            elif current_tag.startswith("@param"):
                parts = current_tag.split()
                name = parts[1] if len(parts) > 1 else ""
                formatted.append(f"- **Parameter `{name}`**: {content}")
            elif current_tag.startswith("@tparam"):
                parts = current_tag.split()
                name = parts[1] if len(parts) > 1 else ""
                formatted.append(f"- **Template Parameter `{name}`**: {content}")
            elif current_tag == "@return":
                formatted.append(f"**🔁 Return value:** {content}")
            elif current_tag == "@note":
                formatted.append(f"> 💡 **Note:** {content}")
            else:
                tag = current_tag.lstrip("@").capitalize()
                formatted.append(f"- **{tag}:** {content}")
            tag_buffer.clear()

        for line in lines:
            stripped = line.strip()

            if stripped in ("/*", "/**", "*/"):
                continue

            stripped = stripped.lstrip("*").strip()
            if not stripped:
                continue
            if stripped.startswith("@"):
                flush_tag()
                parts = stripped.split(maxsplit=2)
                if len(parts) >= 2 and parts[0] in ["@param", "@tparam"]:
                    current_tag = f"{parts[0]} {parts[1]}"
                    tag_buffer = [parts[2]] if len(parts) == 3 else []
                else:
                    current_tag = parts[0]
                    tag_buffer = (
                        [parts[1]]
                        if len(parts) == 2
                        else [" ".join(parts[1:])] if len(parts) > 2 else []
                    )
            else:
                tag_buffer.append(stripped)

        flush_tag()
        return "\n".join(formatted)

    with open(output_path, "w", encoding="utf-8") as f:
        write_header(f, document_meta)

        # Documentation Progress
        if show_progress:
            write_progress(f, todo_stats)

        # Adding Table of Content to Documentation
        f.write("## 📚 Table of Content\n\n")
        for func in functions:
            if highlight_todo:
                comment = func.get("doxygen", "")
                has_todo = highlight_todo and "TODO" in comment
                prefix = "❌ " if has_todo else "✅ "
            else:
                has_todo = False
                prefix = " "
            f.write(f"- [{prefix}{func['name']}](#{func['name'].lower()})\n")
        f.write("\n")

        # Adding Functions Documentation
        for func in functions:
            comment = func.get("doxygen", "")
            if highlight_todo:
                has_todo = highlight_todo and "TODO" in comment
                todo_marker = "❌ " if has_todo else "✅ "
            else:
                todo_marker = " "
                has_todo = False

            file_info = f"<div style='font-size: 12px; color: gray;'>📄 {os.path.basename(func['file'])} (Line {func['startLine']})</div>"

            f.write(f"## {todo_marker}`{func['name']}` <a href='#top' style='float:right; font-size: 12px;'>🔝 Back to Top</a>\n")
            f.write(f"**Signatur:** `{func['return_type']} {func['name']}({func['templateParams']})({func['params']})`\n\n")
            if func.get("doxygen"):
                if has_todo:
                    f.write("> ⚠️ **Warning: Function contains a TODO mark!**\n\n")
                f.write("### 📘 Documentation\n")
                f.write(f"{file_info}\n\n")
                f.write(format_doxygen_comment(func["doxygen"]) + "\n\n")

        # Adding SW-Version at document footer
        version = arguments.get("app_info", {}).get("version", "1.0")
        f.write("\n---\n")
        f.write(f"<div align='right'>SW-Version: {version}</div>\n")

def write_header(f, document_meta):
    """
    writing document header
    """
    # inserting Logo
    logo_path = document_meta.get("logoPath")
    if logo_path:
        f.write(f'<img src="{logo_path}" alt="Logo" style="max-height: 100px;">\n\n')

    # Adding META-Data to Documentation
    f.write(f"# {document_meta['title']}\n\n")
    f.write(f"**Version**: {document_meta.get('version', 'Unknown')}\n")
    f.write(f"**Autor**: {document_meta.get('author', 'Unknown')}\n")
    f.write(f"**Datum**: {document_meta.get('date', 'Unknown')}\n\n")

    # Top Mark
    f.write("""<a id="top"></a>""")

def write_progress(f, todo_stats):
    bar_length = 20
    done_blocks = int((todo_stats["percent_done"] / 100) * bar_length)
    progress_bar_illustration = "█" * done_blocks + "░" * (bar_length - done_blocks)

    f.write("## 📊 Overall Documentation progress\n\n")
    f.write(f'{todo_stats["done_funcs"]} of {todo_stats["total_funcs"]} functions are **finished documented**\n\n')
    f.write(f'`{progress_bar_illustration}` **{todo_stats["percent_done"]}%**\n\n')

    f.write("\n## 🛠️ Detailed TODO-Statistics\n\n")
    f.write(f'- **Brief**: {todo_stats["brief_done"]} / {todo_stats["total_funcs"]} documented\n')
    f.write(f'  `{make_bar(todo_stats["percent_brief_done"])}` **{todo_stats["percent_brief_done"]}%**\n\n')

    f.write(f'- **Template Params**: {todo_stats["tparams_done"]} / {todo_stats["total_tparams"]} documented\n')
    f.write(f'  `{make_bar(todo_stats["percent_tparams_done"])}` **{todo_stats["percent_tparams_done"]}%**\n\n')

    f.write(f'- **Params**: {todo_stats["params_done"]} / {todo_stats["total_params"]} documented\n')
    f.write(f'  `{make_bar(todo_stats["percent_params_done"])}` **{todo_stats["percent_params_done"]}%**\n\n')

    f.write(f'- **Return**: {todo_stats["return_done"]} / {todo_stats["total_funcs"]} documented\n')
    f.write(f'  `{make_bar(todo_stats["percent_return_done"])}` **{todo_stats["percent_return_done"]}%**\n\n')

def make_bar(percent, length=20):
    """
    helper function to setup progress bar in markdown.
    """
    done = int((percent / 100) * length)
    return "█" * done + "░" * (length - done)
