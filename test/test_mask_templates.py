# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.formatter.code_parser import mask_templates


def test_mask_templates_with_nested_templates():
    code = """\
template<typename T>
class MyClass {
    std::vector<std::pair<T, int>> data;
};
"""
    lines = code.splitlines()
    masked, templates = mask_templates(lines[0])  # line with packaged templates

    # expected placeholder of the masked templade
    expected_templates = {
        '__TPL0__': '<typename T>',
    }

    assert masked == 'template__TPL0__'
    assert templates == expected_templates

def test_mask_templates_with_multiple_templates():
    line = "using map = std::map<std::string, std::vector<int>>;"
    masked, templates = mask_templates(line)

    expected_templates = {
        '__TPL0__': '<std::string, std::vector<int>>',
    }

    assert '__TPL0__' in templates
    assert len(templates) == 1
    assert templates == expected_templates
    assert '__TPL0__' in masked
