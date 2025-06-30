
from configSetup.installModules import ensure_modules

ensure_modules([("PyQt5", "PyQt5")])

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame,
)

class ExpandableWidget(QFrame):
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
            # Toggle visibility of the content area and change the symbol
            expanded = self.toggle_button.isChecked()
            self.content_widget.setVisible(expanded)
            self.toggle_button.setText("▾" if expanded else "▸")  # Change the symbol based on expansion state
        
        def setWidgetTitle(self, title):
            self.header_label.setText(title)