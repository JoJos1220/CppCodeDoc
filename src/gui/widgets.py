# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

"""
Specific Non-Standard UI-Widgets implementation.
"""

from configSetup.installModules import ensure_modules

ensure_modules([("PyQt5", "PyQt5")])

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame,
)

class ExpandableWidget(QFrame):
    """
    UI-Element ExpandableWidgets.
    Class function to combine dropdown-elements within a collapsable form.
    """
    def __init__(self, title, content_widget):
        super().__init__()

        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        self.layout = QVBoxLayout(self)

        # Create header for collapsing/expanding
        self.header_layout = QHBoxLayout()
        self.toggle_button = QPushButton("▸")  # Default to right arrow (collapsed)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.clicked.connect(self.toggle_expansion)
        self.header_layout.addWidget(self.toggle_button)

        self.header_label = QLabel(title)
        self.header_layout.addWidget(self.header_label)

        self.layout.addLayout(self.header_layout)

        # Add the content widget (the settings form)
        self.content_widget = content_widget
        self.layout.addWidget(self.content_widget)

        self.content_widget.setVisible(False)  # Initially collapsed

    def toggle_expansion(self):
        """
        Toggle visibility of the content area and change the symbol
        """
        expanded = self.toggle_button.isChecked()
        self.content_widget.setVisible(expanded)
        # Changing the symbol, based on expansion state
        self.toggle_button.setText("▾" if expanded else "▸")

    def set_widget_title(self, title):
        """
        Set the title of the widget
        """
        self.header_label.setText(title)
