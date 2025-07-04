# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

"""
Helper functions for file handling/utilities.
"""

import os

def get_cpp_files(path, arguments):
    """
    function to gather a list of all cpp-based files out of overloaded path.
    If selected recursive, all subdirectorys are also parsed. 
    """
    cpp_files = []
    recursive = bool(arguments["recursive"])

    if os.path.isfile(path):
        if path.endswith((".cpp", ".h", ".hpp", ".cxx", ".ino")):
            cpp_files.append(path)
        return cpp_files
    if os.path.isdir(path):
        if recursive:
            for root, _, files in os.walk(path):
                for file in files:
                    if ( file.endswith(".cpp") or file.endswith(".h") or 
                            file.endswith(".hpp") or file.endswith(".cxx") or
                            file.endswith(".ino")):
                        cpp_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(path):
                full_path = os.path.join(path, file)
                if (os.path.isfile(full_path) and
                        file.endswith((".cpp", ".h", ".hpp", ".cxx", ".ino"))):
                    cpp_files.append(full_path)

        return cpp_files

    # if wether file or directory exists - return nothing-list
    return []
