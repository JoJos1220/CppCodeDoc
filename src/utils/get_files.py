# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

from utils.file_utils import get_cpp_files

def get_files(arguments, config):
    if arguments.file:
        source_files = [arguments.file]
    else:
        source_files = get_cpp_files(config["source_dir"], config)

    return source_files
