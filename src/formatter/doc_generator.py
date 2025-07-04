# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

"""
generation of documentation in html or markdown format is done here.
"""

from formatter.code_parser import (
     extract_functions, insert_comments, replace_comments, make_file_backup)
from formatter.doxygen_generator import generate_doxygen_comment

def generate_documentation(arguments, source_files):
    """
    generating documentation out of source-files and arguments.
    """
    all_functions = []
    readonly = arguments["readonly"]
    doxygen_comments = arguments["headerCommentStyle"]
    backup_path = arguments["backup_path"]

    for file_path in source_files:
        if not readonly:
            if backup_path is not None:
                if not make_file_backup(file_path, backup_path):
                    return f"ERROR while creating Backupdir: {backup_path}"
            insert_comments(file_path, arguments)

        functions = extract_functions(file_path)
        for func in functions:
            generate_doxygen_comment(func)
        all_functions.extend(functions)
        if (doxygen_comments == "doxygen" or doxygen_comments == 'doxygen') and not readonly:
            replace_comments(file_path, functions)

    return all_functions
