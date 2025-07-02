# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import os
import re
import html

def write_html_doc(functions, output_path, arguments, todo_stats):
    document_meta = arguments["document"]
    highlight_todo = document_meta.get("highlightTodo", False)
    show_progress = document_meta.get("showDocProgress", True)

    # Writing Output Document
    with open(output_path, "w", encoding="utf-8") as f:
        logo_html = ""
        logo_path = document_meta.get("logoPath")
        if logo_path:
            logo_html = f'<div style="text-align:left; margin-bottom: 20px;"><img src="file:///{logo_path}" alt="Logo" style="max-height: 100px;"></div>'
        f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{document_meta.get('title', 'Functional Documentation')} - Functional Documentation</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f2f2f2; color: #333; padding: 20px; }}
        h1 {{ color: #004080; text-align: center; }}
        h2 {{ margin-top: 30px; color: #0066cc; }}
        .code-block {{ background: #fff; border: 1px solid #ccc; padding: 10px; font-family: monospace; white-space: pre-wrap; border-radius: 6px; box-shadow: 1px 1px 3px #ccc; }}
        .doxygen-comment {{ background: #e8f0fe; border-left: 4px solid #3367d6; margin-top: 10px; padding: 10px; font-family: monospace; white-space: pre-wrap; border-radius: 5px; display: none; }}
        .doxygen-comment.show {{ display: block; }}
        .doxygen-comment span.brief {{ color: #0b5394; font-weight: bold; }}
        .doxygen-comment span.param {{ color: #38761d; }}
        .doxygen-comment span.return {{ color: #990000; }}
        .doxygen-comment span.note {{ color: #8a2be2; font-style: italic; }}
        .doxygen-comment span.tag {{ color: #999; font-style: italic; }}
        button.toggle-btn {{ margin-top: 5px; margin-bottom: 10px; padding: 5px 10px; border-radius: 4px; border: none; background: #004080; color: white; cursor: pointer; transition: background 0.3s ease; }}
        button.toggle-btn.active {{ background: #28a745; }}
        .print-btn {{ position: fixed; top: 10px; right: 10px; background: #28a745; color: white; border: none; padding: 8px 14px; border-radius: 5px; cursor: pointer; font-size: 14px; }}
        @media print {{ .print-btn, .toggle-btn {{ display: none; }} }}
        ul.toc {{ background: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 1px 1px 5px #aaa; list-style: none; }}
        ul.toc li {{ margin-bottom: 8px; }}
        ul.toc li a {{ text-decoration: none; color: #004080; font-weight: bold; }}
    </style>
    <script>
        function toggleComment(id, button) {{
            const block = document.getElementById(id);
            const isVisible = block.classList.contains('show');
            block.classList.toggle('show', !isVisible);
            button.classList.toggle('active', !isVisible);
            button.innerText = isVisible ? "📘 Show Comments" : "📘 Hide Comments";
        }}
        function printDoc() {{
            window.print();
        }}
    </script>
</head>
<body>
    <a id="top"></a>
    <button class="print-btn" onclick="printDoc()">🖨️ Print</button>
    
    {logo_html}

    <!-- Document Overview -->
    <h1>{document_meta.get('title', 'Funcitonal Documentation')}</h1>
    <p><strong>Version:</strong> {document_meta.get('version', '1.0')}</p>
    <p><strong>Autor:</strong> {document_meta.get('author', 'Unbekannt')}</p>
    <p><strong>Datum:</strong> {document_meta.get('date', 'Unbekannt')}</p>
""")
        if show_progress:
            f.write(f""" 
    <h2>📊 Overall Documentation progress</h2>
    <p>{todo_stats["done_funcs"]} of {todo_stats["total_funcs"]} functions are <strong>finished documented</strong>.</p>
    <div style='background-color: #eee; border-radius: 5px; overflow: hidden; width: 100%; max-width: 400px;'>
        <div style='background-color: #28a745; width: {todo_stats["percent_done"]}%; padding: 5px 0; text-align: center; color: white; font-weight: bold;'>
            {todo_stats["percent_done"]}%
        </div>
    </div>
    <br>
""")
            # Extra-Statistiken schreiben
            f.write(f"""
    <h3 style='margin-top: 40px;'>🛠️ Detailed TODO-Statistics</h3>

    <div style="font-size: 0.9em; color: #555; max-width: 400px;">
        <p><strong>Brief:</strong> {todo_stats["brief_done"]}/{todo_stats["total_funcs"]}</p>
        <div style='background-color: #eee; border-radius: 3px; overflow: hidden; height: 14px; margin-bottom: 10px;'>
            <div style='background-color: #007bff; width: {todo_stats["percent_brief_done"]}%; height: 100%; text-align: right; padding-right: 4px; color: white; font-size: 10px;'>
                {todo_stats["percent_brief_done"]}%
            </div>
        </div>

        <p><strong>Template-Params:</strong> {todo_stats["tparams_done"]}/{todo_stats["total_tparams"]}</p>
        <div style='background-color: #eee; border-radius: 3px; overflow: hidden; height: 14px; margin-bottom: 10px;'>
            <div style='background-color: #ffc107; width: {todo_stats["percent_tparams_done"]}%; height: 100%; text-align: right; padding-right: 4px; color: black; font-size: 10px;'>
                {todo_stats["percent_tparams_done"]}%
            </div>
        </div>

        <p><strong>Params:</strong> {todo_stats["params_done"]}/{todo_stats["total_params"]}</p>
        <div style='background-color: #eee; border-radius: 3px; overflow: hidden; height: 14px; margin-bottom: 10px;'>
            <div style='background-color: #ffc107; width: {todo_stats["percent_params_done"]}%; height: 100%; text-align: right; padding-right: 4px; color: black; font-size: 10px;'>
                {todo_stats["percent_params_done"]}%
            </div>
        </div>

        <p><strong>Return:</strong> {todo_stats["return_done"]}/{todo_stats["total_funcs"]}</p>
        <div style='background-color: #eee; border-radius: 3px; overflow: hidden; height: 14px; margin-bottom: 10px;'>
            <div style='background-color: #17a2b8; width: {todo_stats["percent_return_done"]}%; height: 100%; text-align: right; padding-right: 4px; color: white; font-size: 10px;'>
                {todo_stats["percent_return_done"]}%
            </div>
        </div>
    </div>
""")

            
        f.write("""
    <h2>📚 Table of Content</h2>
    <ul class="toc">
""")
        for func in functions:
            comment = func.get("doxygen", "")
            if highlight_todo:
                has_todo = highlight_todo and "TODO" in comment
                prefix = "❌ " if has_todo else "✅ "
            else:
                prefix = " "
            f.write(f"<li><a href='#{func['name']}'>{prefix}{func['name']}</a></li>\n")
        f.write("</ul>\n")

        for idx, func in enumerate(functions):
            todo_marker = ""
            highlight_style = ""

            comment = func.get("doxygen", "")
            if highlight_todo:
                comment_contains_todo = "TODO" in comment

                if comment_contains_todo:
                    todo_marker = "❌ "
                    highlight_style = "background-color: #fff3cd; border-left: 6px solid red; padding-left: 10px;"
                else:
                    todo_marker = "✅ "
            else:
                todo_marker = " "

            f.write(f"""
            <div style='display: flex; align-items: center; justify-content: space-between; margin-top: 15px;'>
                <h2 id='{func['name']}' style='margin: 0; {highlight_style}'>{todo_marker}{func['name']}</h2>
                <a href='#top' style='font-size: 14px; color: #0066cc; text-decoration: none;'>🔝 Back to Top</a>
            </div>
            """)
            if todo_marker == "❌ ":
                f.write("<div style='margin-top: 8px; color: #856404; background-color: #fff3cd; border: 1px solid #ffeeba; padding: 10px; border-radius: 4px;'>⚠️ <strong>Warning:</strong> Function contains a TODO mark!</div>\n")
            
            f.write(f"<div class='code-block'>{html.escape(func['return_type'])} {html.escape(func['name'])}({html.escape(func['params'])})</div>\n")
            
            if func.get("doxygen"):
                file_info = f"<div style='font-size: 12px; color: gray;'>📄 {os.path.basename(func['file'])} (Line {func['startLine']})</div>"
                comment = func["doxygen"]
                tag_classes = {
                    "@brief": "brief",
                    "@tparam": "param",
                    "@param": "param",
                    "@return": "return",
                    "@note": "note"
                }

                for tag, css_class in tag_classes.items():
                    comment = comment.replace(tag, f"<span class='{css_class}'>{tag}</span>")

                def replace_unknown_tags(match):
                    tag = f"@{match.group(1)}"
                    if tag not in tag_classes:
                        return f"<span class='tag'>{tag}</span>"
                    return tag
                
                comment = re.sub(r'@(\w+)', replace_unknown_tags, comment)
                
                comment_id = f"comment_{idx}"
                f.write(f"<button class='toggle-btn active' onclick=\"toggleComment('{comment_id}', this)\">📘 Hide comments</button>\n")
                f.write(f"<div class='doxygen-comment show' id='{comment_id}'>{file_info}{comment}</div>\n")

        f.write(f"""
    <div style="position: fixed; bottom: 10px; right: 10px; font-size: 12px; color: #666;">
        SW-Version: {arguments.get("app_info", {}).get("version", "1.0")}
    </div>
</body></html>
""")
