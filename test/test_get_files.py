# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys, os
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.utils.get_files import get_files 

class MockArguments:
    def __init__(self, file=None):
        self.file = file

@patch("src.utils.get_files.get_cpp_files")
def test_get_files_from_directory(mock_get_cpp_files):
    mock_get_cpp_files.return_value = ["main.cpp", "helper.h"]
    arguments = MockArguments(file=None)
    config = {
        "source_dir": "/src",
        "recursive": False,
    }

    result = get_files(arguments, config)

    mock_get_cpp_files.assert_called_once_with("/src", config)
    assert result == ["main.cpp", "helper.h"]