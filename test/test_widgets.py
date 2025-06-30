# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys, os, pytest
from PyQt5.QtWidgets import QApplication, QLabel

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.gui.widgets import ExpandableWidget

# Singleton QApplication starting for all Tests
@pytest.fixture(scope="session", autouse=True)
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.mark.skipif(
    not os.environ.get("DISPLAY"),
    reason="Skipping GUI test: DISPLAY not available (headless or act environment)"
)
def test_expandable_widget_initial_state(app):
    label = QLabel("Testinhalt")
    widget = ExpandableWidget("Titel", label)

    assert not label.isVisible()
    assert widget.toggle_button.text() == "▸"
    assert widget.header_label.text() == "Titel"


@pytest.mark.skipif(
    not os.environ.get("DISPLAY"),
    reason="Skipping GUI test: DISPLAY not available (headless or act environment)"
)
def test_expandable_widget_toggle_behavior(app):
    label = QLabel("Inhalt")
    widget = ExpandableWidget("MeinWidget", label)

    widget.show()
    widget.toggle_button.click()

    assert label.isVisible()
    assert widget.toggle_button.text() == "▾"

    widget.toggle_button.click()
    assert not label.isVisible()
    assert widget.toggle_button.text() == "▸"


@pytest.mark.skipif(
    not os.environ.get("DISPLAY"),
    reason="Skipping GUI test: DISPLAY not available (headless or act environment)"
)
def test_expandable_widget_title_set(app):
    label = QLabel("...")
    widget = ExpandableWidget("Start", label)

    widget.setWidgetTitle("Neu")
    assert widget.header_label.text() == "Neu"
