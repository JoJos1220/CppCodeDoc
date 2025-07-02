# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys
import os
import pytest
from PyQt5.QtWidgets import QLabel, QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.gui.dialogs import ContentDialogWindow

# skipping test if no display is available!(e.g. in act or Xvfb environment)
@pytest.mark.skipif(
    not os.environ.get("DISPLAY"),
    reason="Skipping GUI test: DISPLAY not available (headless or act environment)"
)
def test_dialog_creates_window():
    app = QApplication(sys.argv)
    content = QLabel("ContentDialogWindow")
    dialog = ContentDialogWindow(content_widget=content, title="TestWindow", size=(400, 300))

    assert dialog.windowTitle() == "TestWindow"
    assert dialog.width() == 400
    assert dialog.height() == 300
    assert dialog.layout().count() == 1
    assert dialog.layout().itemAt(0).widget().text() == "ContentDialogWindow"
    app.quit()
