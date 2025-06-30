# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import os, sys, argparse, subprocess, re
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ----- Optional: Automatisch PyQt5 installieren -----
from configSetup.installModules import ensure_modules
ensure_modules([("PyQt5", "PyQt5"),
                ("requests", "requests"),
                ("yaml", "pyYAML"),
                ("markdown", "markdown")])
import requests, yaml

from markdown import markdown

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QFileDialog, QLineEdit, QLabel, QCheckBox, QTextEdit,
    QComboBox, QScrollArea, QGroupBox, QMessageBox, QSizePolicy,
    QTextBrowser, QShortcut
)
from PyQt5.QtGui import QPixmap, QIcon, QFont, QDesktopServices, QKeySequence
from PyQt5.QtCore import Qt, QSettings, QUrl, QSize

from utils.app_info import (__GITHUB_REPO__, __version__, __title__,
    __description__, __author__, __license_text__,
    __license_header__, __PAYPAL_URL__, __KOFI_URL__, __GITHUB_URL__, __file_extension__
)
from streamLogger.log_setup import logger
from utils.file_utils import get_cpp_files
from formatter.doc_generator import generate_documentation
from formatter.code_parser import check_input_string_looks_like_path
from generator.save_report import save_documentation
from configSetup.configSetup import load_config, resource_path
from utils.get_files import get_files

# ========================== SETUP Global Logging instance ==========================
logName = "CppCodeDoc.log"
loggingDir=os.path.join(os.path.dirname(__file__), "log")
loggingDirectory = os.path.join(loggingDir, logName)

logger.setup_logging(log_name=logName, log_dir=loggingDir)
logger.log("Logging setup complete", "info")

# ========================== GUI PART ==========================
class DocGeneratorApp(QWidget):
    from gui.translator import Translator
    from gui.widgets import ExpandableWidget
    from gui.dialogs import ContentDialogWindow

    def __init__(self, config_path=""):
        super().__init__()
        # Logging Class Setup
        DocGeneratorApp.instance = self
        logger.set_app_class(self)
        logger.log("Application started", "info")

        # Loading Preference Settings from PyQT5 QSettings
        self.settings = QSettings(f"{__title__}", f"{__title__}")
        pref_config, pref_lang, pref_ui_mode =  self.load_preferences()

        # Shortcut interaction
        f1_shortcut = QShortcut(QKeySequence("F1"), self)
        f1_shortcut.activated.connect(self.show_help_window)

        # Translation Setup with default English
        self.translator = self.Translator(lang=pref_lang)

        self.configChanged = False
        self.is_dark_mode = pref_ui_mode

        self.icon_path = resource_path("../utils/icon/icon.ico", "assets/icon.ico")
        print(f"Icon Path: {self.icon_path}")    
        if os.path.exists(self.icon_path):
            self.setWindowIcon(QIcon(self.icon_path))
        else:
            logger.log(f"Icon Path can't be found: {self.icon_path}", "warning")

        self.setWindowTitle(f"{__title__} v{__version__} by {__author__}")
        self.setGeometry(100, 100, 1280, 800)

        # Main Window Layout
        main_layout = QHBoxLayout()

        self.log_output = QTextEdit()
        self.log_output.setObjectName("logOutput")
        self.log_output.setReadOnly(True)

        # Tabs Layout
        self.tabs = QTabWidget()

        self.start_tab = self.create_start_tab()
        self.settings_tab = self.create_settings_tab()
        self.log_tab = self.create_log_tab()
        self.about_tab = self.create_about_tab()
        self.help_tab = self.create_help_tab(resource_path("../../help.md", "assets/help.md"))

        self.tabs.addTab(self.start_tab, self.translator.translate("mainTabs.start"))
        self.tabs.addTab(self.settings_tab, self.translator.translate("mainTabs.settings"))
        self.tabs.addTab(self.log_tab, self.translator.translate("mainTabs.log"))
        self.tabs.addTab(self.about_tab, self.translator.translate("mainTabs.about"))
        self.tabs.addTab(self.help_tab, self.translator.translate("mainTabs.help"))
        self.tabs.setTabToolTip(self.tabs.indexOf(self.help_tab), self.translator.translate("mainTabs.helpToolTip"))

        main_layout.addWidget(self.tabs)

        logger.log("App started (GUI Mode)", "info")

        # ProjectLogo and Sponsorship Icons -------------------------------------------------------------------------------
        box_widget = QWidget()
        box_widget.setFixedWidth(410) 
        box_layout = QVBoxLayout(box_widget)
        box_layout.setContentsMargins(0, 0, 0, 0)
        box_layout.setSpacing(0)
        
        # Button mit Icon oberhalb des Logos
        spacer = QWidget()
        spacer.setFixedHeight(75)
        box_layout.addWidget(spacer)

        dark_mode_widget = QWidget()
        dark_mode_layout = QVBoxLayout(dark_mode_widget)
        dark_mode_layout.setContentsMargins(0, 0, 0, 0)
        dark_mode_layout.setSpacing(5)  # Kleiner Abstand zwischen Label und Button

        self.another_label = QLabel("Toggle Dark/Light Mode")
        dark_mode_layout.addWidget(self.another_label)

        self.switch_darkMode_button = QPushButton()
        self.switch_darkMode_button.setIcon(QIcon(resource_path("../generator/img/DarkMode.svg", "assets/DarkMode.svg")))  # Hier das gewünschte Icon setzen
        self.switch_darkMode_button.setIconSize(QSize(48, 48))  # Maximal 48x48px
        self.switch_darkMode_button.setFixedSize(48, 48)  # Buttongröße auf 48x48px setzen

        # Button-Aktion definieren (optional)
        self.switch_darkMode_button.clicked.connect(lambda: self.toggle_darkMode_click())

        dark_mode_layout.addWidget(self.switch_darkMode_button, alignment=Qt.AlignHCenter)
        dark_mode_layout.addStretch()

        box_layout.addWidget(dark_mode_widget, alignment=Qt.AlignHCenter)

        # Implementation of Projcect Logo, alignged to right/center of the window
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        image_path = resource_path("../generator/img/Reference.png", "assets/Reference.png")
        print(f"Logo Path: {image_path}")
        if os.path.exists(image_path):
            logo_pixmap = QPixmap(image_path)
            self.logo_label.setPixmap(logo_pixmap.scaled(400, 400, aspectRatioMode=1))
        else:
            logger.log(f"Logo Path can't be found: {image_path}", "warning")
        
        box_layout.addWidget(self.logo_label, alignment=Qt.AlignHCenter)

        paypal_icon_path = resource_path("../generator/img/paypal.svg", "assets/paypal.svg")
        kofi_icon_path = resource_path("../generator/img/Ko-fi.svg", "assets/Ko-fi.svg")
        github_icon_path = resource_path("../generator/img/github.svg", "assets/github.svg")

        self.paypal_label = self.create_icon_label(paypal_icon_path, __PAYPAL_URL__)
        self.kofi_label = self.create_icon_label(kofi_icon_path, __KOFI_URL__)
        self.github_label = self.create_icon_label(github_icon_path, __GITHUB_URL__)
        
        # Beide Icons exakt gleich groß & festgesetzt
        for label in [self.paypal_label, self.kofi_label, self.github_label]:
            label.setFixedSize(50, 50)
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        icon_row = QHBoxLayout()
        icon_row.setSpacing(0)
        icon_row.setContentsMargins(0, 0, 0, 0)
        icon_row.addStretch()
        icon_row.addWidget(self.paypal_label)
        icon_row.addWidget(self.kofi_label)
        icon_row.addWidget(self.github_label)
        icon_row.addStretch()

        box_layout.addLayout(icon_row)

        # -- Box in main layout einfügen
        main_layout.addWidget(box_widget)

        self.setLayout(main_layout)

        self.switch_darkMode_click()

        # Initialize Configuration - load Configfile at start
        config_path = (
            config_path
            if config_path
            else pref_config
        )
        self.loadConfigSettingsFromFile(config_path)

    def toggle_darkMode_click(self):
        self.is_dark_mode = not self.is_dark_mode
        self.switch_darkMode_click()

    def switch_darkMode_click(self):
        if self.is_dark_mode:
            # Dark Mode aktivieren
            self.setStyleSheet("""
                QWidget {
                    background-color: #2e2e2e;
                    color: #ffffff;
                    font-size: 12pt;
                }
                QPushButton {
                    background-color: #444444;
                    color: #ffffff;
                    height: 50px;
                    font-size: 12pt;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #5c5c5c;
                }
                QLineEdit, QTextEdit, QComboBox, QScrollArea {
                    background-color: #3a3a3a;
                    color: #ffffff;
                    height: 50px;
                    font-size: 12pt;
                    border: 1px solid #666666;
                    border-radius: 5px;
                }
                QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                    border: 1px solid #aaaaaa;
                }
                QComboBox::drop-down {
                    width: 35px;
                }
                QTextEdit#logOutput {
                    background-color: #3a3a3a;
                    color: #ffffff;
                    font-size: 10pt;
                    border: 1px solid #666666;
                    border-radius: 5px;
                }
                QLabel {
                    color: #ffffff;
                    font-size: 12pt;
                }
                QCheckBox {
                    color: #ffffff;
                    font-size: 12pt;
                }
                QGroupBox {
                    font-size: 12pt;
                    border: 1px solid #666666;
                    border-radius: 5px;
                    margin: 10px;
                    padding: 10px;
                }
                QTabBar::tab {
                    background-color: #2e2e2e;
                    color: #cccccc;
                    font-size: 12pt;
                    padding: 5px;
                    border: 1px solid #444444;
                    border-bottom: none;
                    min-width: 50px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #444444;
                    color: #ffffff;
                    border: 1px solid #666666;
                    border-bottom: none;
                }
                QTabBar::tab:hover {
                    background-color: #3a3a3a;
                    color: #ffffff;
                }
                QTabWidget::pane {
                    border: 1px solid #666666;
                    top: -1px;  /* Pane an Tab anschließen */
                    background-color: #2e2e2e;
                    border-radius: 5px;
                }
                QScrollArea {
                    background-color: #3a3a3a;
                    border: 1px solid #666666;
                }
            """)
            self.is_dark_mode = True
        else:
            # Zurück zu Light Mode
            self.setStyleSheet("""
                QWidget {
                    background-color: #f4f4f4;
                    color: #333333;
                    font-size: 12pt;
                }
                QPushButton {
                    background-color: #e2e2e2;
                    color: #333333;
                    height: 50px;
                    font-size: 12pt;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #c1c1c1;
                }
                QLineEdit, QTextEdit, QComboBox, QScrollArea {
                    background-color: #ffffff;
                    color: #333333;
                    height: 50px;
                    font-size: 12pt;
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                }
                QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                    border: 1px solid #666666;
                }
                QComboBox::drop-down {
                    width: 35px;  /* Breite des Dropdown-Buttons */
                }          
                QTextEdit#logOutput {
                    background-color: #ffffff;  /* White background for text output */
                    color: #333333;  /* Dark text */
                    font-size: 10pt;
                    border: 1px solid #cccccc;  /* Light grey border */
                    border-radius: 5px;  /* Rounded corners */
                }
                QLabel {
                    color: #333333;
                    font-size: 12pt;
                }
                QCheckBox {
                    color: #333333;
                    font-size: 12pt;
                }
                QGroupBox {
                    font-size: 12pt;
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    margin: 10px;
                    padding: 10px;
                }
                QTabWidget {
                    background-color: #2e2e2e;
                    border: 1px solid #666666;
                }
                QTabWidget::pane {
                    border: none;
                }            
                QTabBar::tab {
                    background-color: #e2e2e2;
                    color: #333333;
                    font-size: 12pt;
                    padding: 5px;
                    border: 1px solid #cccccc;
                    border-bottom: none;
                    min-width: 50px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #c1c1c1;
                    color: #333333;
                    border: 1px solid #aaaaaa;
                    border-bottom: none;
                }
                QTabBar::tab:hover {
                    background-color: #d1d1d1;
                    color: #000000;
                }
                QScrollArea {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                }
            """)
            self.is_dark_mode = False
                
    def closeEvent(self, event):
        if self.configChanged:
            box = QMessageBox()
            box.setIcon(QMessageBox.Warning)
            box.setWindowTitle("Unsaved Changes detected")
            box.setWindowIcon(QIcon(self.icon_path))
            box.setText("Some changes has been made to the configuration.\nDo you want to save them?")
            box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            box.setDefaultButton(QMessageBox.No)

            result = box.exec()
            if result == QMessageBox.Yes:
                self.save_config_to_yaml()
                event.accept()
            else:
                event.accept()
        else:
            event.accept()

        self.save_preferences(self.config_path_input.text(), self.translator.lang, self.is_dark_mode)
        
    def load_preferences(self):
        config_file = self.settings.value("config_file", "", type=str)
        lang = self.settings.value("language", "en", type=str)
        dark_mode = self.settings.value("dark_mode", False, type=bool)
        return config_file, lang, dark_mode

    def save_preferences(self, config_file, lang, dark_mode):
        self.settings.setValue("config_file", config_file)
        self.settings.setValue("language", lang)
        self.settings.setValue("dark_mode", dark_mode)  

    def save_config_to_yaml(self):
        # Bevor saving, updating UI Values
        self.updateConfigFromUserInput()

        # Öffne den Datei-Explorer, um einen Speicherort und Dateinamen auszuwählen
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setNameFilter(f"CppCodeDoc files (*{__file_extension__})")  # Using setNameFilter instead of setFilter
        file_dialog.setDefaultSuffix(f"{__file_extension__}")

        # Zeigt den Dialog und speichert den ausgewählten Pfad
        file_path, _ = file_dialog.getSaveFileName(self, "Save Configuration", "", f"CPPCodeDoc files (*{__file_extension__})")

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as yaml_file:
                    yaml_file.write(__license_header__)
                    yaml_file.write('\n\n')
                    yaml.dump(self.config, yaml_file, default_flow_style=False, allow_unicode=True)
                logger.log(f"New configuration saved to {file_path}", "info")
            except Exception as e:
                logger.log(f"Error saving new configuration: {e}", "warning")
        else:
            logger.log("No file selected. Configuration not saved.", "info")

    def create_icon_label(self, icon_path, url):
        label = QLabel()
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            label.setPixmap(pixmap.scaled(38, 38, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logger.log(f"Icon Path can't be found: {icon_path}", "warning")
        label.setCursor(Qt.PointingHandCursor)
        label.mousePressEvent = lambda event: self.open_url(url)
        return label
    
    def open_url(self, url):
        # Stelle sicher, dass URL valide ist
        if url and isinstance(url, str) and url.startswith(('http://', 'https://')):
            QDesktopServices.openUrl(QUrl(url))
        else:
            logger.log(f"Invalid URL executed: {url}", "warning")

    def create_start_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel(""))  # Keep Spacing

        self.config_path_input = QLineEdit()
        self.config_path_input.setPlaceholderText(self.translator.translate("startTab.ConfigPathPlaceHolder"))
        self.config_path_input.textChanged.connect(lambda: self._configChanged())
        layout.addWidget(self.config_path_input)

        # Button and save button for config file has been changed
        config_layout = QHBoxLayout()

        self.select_configFile_button = QPushButton(self.translator.translate("startTab.SelectConfigFileButton"))
        self.select_configFile_button.clicked.connect(lambda: self.select_file("config","file"))
        config_layout.addWidget(self.select_configFile_button)

        # 💾 Save-Config-File-Button
        self.save_config_button = QPushButton(self.translator.translate("startTab.SaveConfigFileButton"))
        self.save_config_button.clicked.connect(self.save_config_to_yaml)
        config_layout.addWidget(self.save_config_button)

        layout.addLayout(config_layout)

        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText(self.translator.translate("startTab.FileInputPlaceHolder"))
        self.file_input.textChanged.connect(lambda: self._configChanged())
        layout.addWidget(self.file_input)

        button_layout = QHBoxLayout()

        self.select_sourceFile_button = QPushButton(self.translator.translate("startTab.SelectSourceFileButton"))
        self.select_sourceFile_button.clicked.connect(lambda: self.select_file("source","file"))
        button_layout.addWidget(self.select_sourceFile_button)

        self.select_sourceDir_button = QPushButton(self.translator.translate("startTab.SelectSourceDirButton"))
        self.select_sourceDir_button.clicked.connect(lambda: self.select_file("source","dir"))
        button_layout.addWidget(self.select_sourceDir_button)

        layout.addLayout(button_layout)
        layout.addWidget(QLabel(""))  # Keep Spacing

        self.generate_button = QPushButton(self.translator.translate("startTab.CreateDocButton"))
        self.generate_button.clicked.connect(self.generate_documentation)
        layout.addWidget(self.generate_button)

        self.status_label = QLabel(self.translator.translate("states.ready"))
        layout.addWidget(self.status_label)

        # Button to open Output-Directory of the Documentation
        self.open_outputDoc_dir_button = QPushButton(self.translator.translate("startTab.OpenOutputDirButton"))
        self.open_outputDoc_dir_button.setVisible(False)
        self.open_outputDoc_dir_button.clicked.connect(lambda: self.open_output_directory("doc"))
        layout.addWidget(self.open_outputDoc_dir_button)  # ✅ direkt ins main_layout

        tab.setLayout(layout)
        return tab

    def create_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()  # Inhalt der ScrollArea
        scroll_content_layout = QVBoxLayout()

        # ================= General Settings =================
        general_group = QWidget()
        general_layout = QVBoxLayout()

        # Translation
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([self.translator.translate("settingsTab.EnglishSuffix"), self.translator.translate("settingsTab.GermanSuffix")])
        self.lang_combo.setCurrentIndex(self.translator.get_current_language())
        self.lang_combo.currentTextChanged.connect(self.change_language)
        self.lang_combo_label = QLabel(self.translator.translate("settingsTab.LangComboLabel"))
        layout.addWidget(self.lang_combo_label)
        layout.addWidget(self.lang_combo)

        # Readonly checkbox
        self.readonly_checkbox = QCheckBox(self.translator.translate("settingsTab.ReadOnlyCheckBox"))
        self.readonly_checkbox.stateChanged.connect(lambda: self._configChanged())
        general_layout.addWidget(self.readonly_checkbox)

        # Recursive Source Directory parsing checkbox
        self.recursive_checkbox = QCheckBox(self.translator.translate("settingsTab.RecursiveCheckbox"))
        self.recursive_checkbox.stateChanged.connect(lambda: self._configChanged())
        general_layout.addWidget(self.recursive_checkbox)

        # (optional) Backup directory input + label
        self.backup_dir_input = QLineEdit()
        self.backup_dir_input.setPlaceholderText(self.translator.translate("settingsTab.BackupDirPlaceHolder"))
        self.backup_dir_input.textChanged.connect(lambda: self._configChanged())
        self.backup_dir_label = QLabel(self.translator.translate("settingsTab.BackupDirLabel"))
        general_layout.addWidget(self.backup_dir_label)
        general_layout.addWidget(self.backup_dir_input)

        # optional Backup select directory button
        self.select_backupDir_button = QPushButton(self.translator.translate("settingsTab.BackupDirButton"))
        self.select_backupDir_button.clicked.connect(lambda: self.select_file("backup", "dir"))
        general_layout.addWidget(self.select_backupDir_button)

        general_group.setLayout(general_layout)

        self.general_expandable = self.ExpandableWidget(self.translator.translate("settingsTab.GeneralSettingsExpandable"), general_group)
        scroll_content_layout.addWidget(self.general_expandable)

        # ================= Document Settings =================
        document_group = QWidget()
        document_layout = QVBoxLayout()

        # Document Highlight ToDo Comments in Report Checkbox
        self.highlightToDo = QCheckBox(self.translator.translate("settingsTab.HighlightToDoCheckbox"))
        self.highlightToDo.stateChanged.connect(lambda: self._configChanged())
        document_layout.addWidget(self.highlightToDo)

        # Document Show Documentation Progress Checkbox
        self.showDocProgress = QCheckBox(self.translator.translate("settingsTab.showDocProgressCheckbox"))
        self.showDocProgress.stateChanged.connect(lambda: self._configChanged())
        document_layout.addWidget(self.showDocProgress)

        # Document title input
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(self.translator.translate("settingsTab.titlePlaceHolder"))
        self.title_input.textChanged.connect(lambda: self._configChanged())
        self.title_input_label = QLabel(self.translator.translate("settingsTab.titleLabel"))
        document_layout.addWidget(self.title_input_label)
        document_layout.addWidget(self.title_input)

        # Document version input
        self.version_input = QLineEdit()
        self.version_input.setPlaceholderText(self.translator.translate("settingsTab.docVersionPlaceHolder"))
        self.version_input.textChanged.connect(lambda: self._configChanged())
        self.version_input_label = QLabel(self.translator.translate("settingsTab.docVersionLabel"))
        document_layout.addWidget(self.version_input_label)
        document_layout.addWidget(self.version_input)

        # Document author input
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText(self.translator.translate("settingsTab.docAuthorPlaceHolder"))
        self.author_input.textChanged.connect(lambda: self._configChanged())
        self.author_input_label = QLabel(self.translator.translate("settingsTab.docAuthorLabel"))
        document_layout.addWidget(self.author_input_label)
        document_layout.addWidget(self.author_input)

        # Document date input
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText(self.translator.translate("settingsTab.docDatePlaceHolder"))
        self.date_input.textChanged.connect(lambda: self._configChanged())
        self.date_input_label = QLabel(self.translator.translate("settingsTab.docDateLabel"))
        document_layout.addWidget(self.date_input_label)
        document_layout.addWidget(self.date_input)

        # Document logoPath input
        self.logo_path_input = QLineEdit()
        self.logo_path_input.setPlaceholderText(self.translator.translate("settingsTab.docLogoPlaceHolder"))
        self.logo_path_input.textChanged.connect(lambda: self._configChanged())
        self.logo_path_input_label = QLabel(self.translator.translate("settingsTab.docLogoLabel"))
        document_layout.addWidget(self.logo_path_input_label)
        document_layout.addWidget(self.logo_path_input)

        document_group.setLayout(document_layout)

        self.document_expandable = self.ExpandableWidget(self.translator.translate("settingsTab.DocSettingsExpandable"), document_group)
        scroll_content_layout.addWidget(self.document_expandable)

        # ================= Output Settings =================
        output_group = QWidget()
        output_layout = QVBoxLayout()

        # Output format input (ComboBox for multiple formats)
        self.output_format_input = QComboBox()
        self.output_format_input.addItems([self.translator.translate("settingsTab.HMTLprefix"), self.translator.translate("settingsTab.MDprefix"), self.translator.translate("settingsTab.Allprefix")])  # Dropdown with 'md' and 'html' options
        self.output_format_input.currentTextChanged.connect(lambda: self._configChanged())
        self.output_format_input_label = QLabel(self.translator.translate("settingsTab.OutputFormatInputLabel"))
        output_layout.addWidget(self.output_format_input_label)
        output_layout.addWidget(self.output_format_input)

        # Comment Style default / doxygen
        self.header_comment_style = QComboBox()
        self.header_comment_style.addItems([self.translator.translate("settingsTab.Doxygenprefix"), self.translator.translate("settingsTab.Defaultprefix")])
        self.header_comment_style.currentTextChanged.connect(lambda: self._configChanged())
        self.header_comment_style_label = QLabel(self.translator.translate("settingsTab.HeaderCommentStyleLabel"))
        output_layout.addWidget(self.header_comment_style_label)
        output_layout.addWidget(self.header_comment_style)

        # Output path input
        self.output_path_input = QLineEdit()
        self.output_path_input.setPlaceholderText(self.translator.translate("settingsTab.OutputPathInputPlaceholder"))
        self.output_path_input.textChanged.connect(lambda: self._configChanged())
        self.output_path_input_label = QLabel(self.translator.translate("settingsTab.OutputPathInputLabel"))
        output_layout.addWidget(self.output_path_input_label)
        output_layout.addWidget(self.output_path_input)

        # Output path select directory button
        self.select_outputDir_button = QPushButton(self.translator.translate("settingsTab.OutputDirButton"))
        self.select_outputDir_button.clicked.connect(lambda: self.select_file("output", "dir"))
        output_layout.addWidget(self.select_outputDir_button)

        output_group.setLayout(output_layout)

        self.output_expandable = self.ExpandableWidget(self.translator.translate("settingsTab.OutputSettingsExpandable"), output_group)
        scroll_content_layout.addWidget(self.output_expandable)

        # Apply scrollable content
        scroll_content.setLayout(scroll_content_layout)
        scroll_area.setWidget(scroll_content)

        layout.addWidget(scroll_area)  # Add the scroll area to the main layout

        tab.setLayout(layout)
        return tab

    def toggle_group(self, group: QGroupBox):
        """Toggles visibility of the group."""
        group.setVisible(not group.isVisible())

    def _configChanged(self):
        self.configChanged = True

    def create_log_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.log_output)

        # Button to open Output-Directory of the log
        self.open_outputLog_dir_button = QPushButton(self.translator.translate("loggingTab.OpenOutputLogDirButton"))
        self.open_outputLog_dir_button.clicked.connect(lambda: self.open_output_directory("log"))
        layout.addWidget(self.open_outputLog_dir_button) 

        tab.setLayout(layout)
        return tab

    def append_log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_output.append(f"[{timestamp}] {message}")

    def create_about_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"<b>{__title__}</b>"))
        layout.addWidget(QLabel(f"Software Version: {__version__}"))
        layout.addWidget(QLabel(f"Author: {__author__}"))
        #Adding Repo label with URL
        self.repoURLLabel = QLabel(f'Repository: <a href="{__GITHUB_URL__}">{__GITHUB_URL__}</a>')
        self.repoURLLabel.setOpenExternalLinks(True)
        self.repoURLLabel.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.repoURLLabel.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.repoURLLabel)

        # layout.addWidget(QLabel(""))  # Keep Spacing
        # Erstelle ein klickbares Label:
        self.changelogLabel = QLabel('Changelog: <a href="#">Changelog</a>')
        self.changelogLabel.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.changelogLabel.setOpenExternalLinks(False)  # Wir wollen nicht, dass es eine echte URL öffnet
        self.changelogLabel.setCursor(Qt.PointingHandCursor)

        # Signal verbinden: Klick auf das Label öffnet das Changelog-Fenster
        self.changelogLabel.linkActivated.connect(self.show_changelog_window)

        layout.addWidget(self.changelogLabel)

        desc = QTextEdit()
        desc.setReadOnly(True)
        desc.setText(__description__)
        layout.addWidget(desc)

        # --- Update-Check Button ---
        update_btn = QPushButton("🔄 Check for Update")
        update_btn.clicked.connect(self.check_for_update)
        layout.addWidget(update_btn)

        layout.addWidget(QLabel("<b>License:</b>"))
        license_text = QTextEdit()
        license_text.setReadOnly(True)
        license_text.setPlainText(__license_text__)
        license_text.setMaximumHeight(300)  # optional, um es kompakt zu halten
        layout.addWidget(license_text)

        tab.setLayout(layout)
        return tab

    def create_help_tab(self, md_file_path: str, fallback_text: str = "Content not available."):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setOpenLinks(True)

        if os.path.exists(md_file_path):
            with open(md_file_path, "r", encoding="utf-8") as file:
                md_content = file.read()

                def heading_with_id(match):
                    text = match.group(1).strip()
                    level = match.group(0).count("#")
                    anchor = re.sub(r"[^\w\- ]", "", text).replace(" ", "-").lower()
                    return f'<h{level} id="{anchor}">{text}</h{level}>'

                md_content = re.sub(r"^#{1,6} (.+)", heading_with_id, md_content, flags=re.MULTILINE)

                html = markdown(md_content, extensions=["extra", "sane_lists"])
                css = """
                    <style>
                    body { font-family: "Segoe UI Emoji", "Arial", sans-serif; }
                    </style>
                    """
                html = css + html
                browser.setHtml(html.encode("utf-8").decode("utf-8"))
        else:
            browser.setText(fallback_text)

        font = QFont("Segoe UI Emoji")
        font.setPointSize(10)
        browser.setFont(font)

        layout.addWidget(browser)
        return widget

    def show_help_window(self):
        logger.log("Opening Help window", "info")
        help_content = self.create_help_tab(resource_path("../../help.md", "assets/help.md"))
        self.help_dialog = self.ContentDialogWindow(help_content, title="Help")
        self.help_dialog.show()

    def show_changelog_window(self):
        logger.log("Opening Changelog window", "info")
        help_content = self.create_help_tab(resource_path("../../changelog.md", "assets/changelog.md"))
        self.help_dialog = self.ContentDialogWindow(help_content, title="Changelog")
        self.help_dialog.show()

    def select_file(self, target="source", mode="file"):  
        if mode == "file":
            if target == "source":
                file_path, _ = QFileDialog.getOpenFileName(
                    self, f'Select {target.capitalize()} file', '', 'C++ Files (*.cpp *.h *.hpp *.cxx *.ino)')
            elif target == "config":
                file_path, _ = QFileDialog.getOpenFileName(
                    self, f'Select {target.capitalize()} file', '', f'CppCodeDoc Files (*{__file_extension__})')
            else:
                logger.log(f"Invalid target/mode selected: {target} / {mode}", "warning")
        elif mode == "dir":
            file_path = QFileDialog.getExistingDirectory(
                self, f'Select {target.capitalize()} Directory', '')
        else:
            logger.log(f"Invalid mode selected: {mode}", "warning")

        if file_path:
            if os.path.isdir(file_path):
                logger.log(f"{target.capitalize()} Directory selected: {file_path}", "info")
            elif os.path.isfile(file_path):
                logger.log(f"{target.capitalize()} File selected: {file_path}", "info")
            else:
                logger.log(f"{target.capitalize()} file is whether file or directory: {file_path}", "warning")
                return

            if target == "source":
                self.file_input.setText(file_path)
            elif target == "output":
                self.output_path_input.setText(file_path)
            elif target == "backup":
                self.backup_dir_input.setText(file_path)
            elif target == "config":
                self.config_path_input.setText(file_path)
                self.loadConfigSettingsFromFile(file_path)
            else:
                logger.log(f"Unknown target: {target}", "warning")

        else:
            # Optional: Falls kein Pfad ausgewählt wurde
            logger.log(f"No {target.capitalize()} File/Directory selected: {file_path}", "info")

    def loadConfigSettingsFromFile(self, path):
        self.config, errors = load_config(path)
        self.config["app_info"] = {
            "version": __version__,
            "title": __title__,
            "description": __description__,
            "author": __author__
        }
        if errors:
            for err in errors:
                logger.log(f"Error while parsing/loading config file: {err}", "warning")
                box = QMessageBox()
                box.setIcon(QMessageBox.Warning)
                box.setWindowTitle("Update config file failed!")
                box.setWindowIcon(QIcon(self.icon_path))
                box.setText(
                    f"Error while parsing/loading config file: {err}"
                )
                box.exec()
        logger.log(f"Config loaded from: {self.config['config_path']}", "info")
        self.update_settings_tab_from_config()

    def update_settings_tab_from_config(self):
        # Setze die Konfigurationswerte in die entsprechenden Eingabefelder
        if "readonly" in self.config:
            self.readonly_checkbox.setChecked(self.config["readonly"])
            self.configChanged = False

        if "recursive" in self.config:
            self.recursive_checkbox.setChecked(self.config["recursive"])
            self.configChanged = False

        if "output_format" in self.config:
            formats = self.config["output_format"]
            if(len(formats) < 2):
                if(formats[0] == "html"):
                    self.output_format_input.setCurrentIndex(0)
                if(formats[0] == "md"):
                    self.output_format_input.setCurrentIndex(1)
            else:
                self.output_format_input.setCurrentIndex(2)

        if "headerCommentStyle" in self.config:
            self.header_comment_style.setCurrentText(self.config["headerCommentStyle"])

        if "output_path" in self.config:
            self.output_path_input.setText(self.config["output_path"])

        if "source_dir" in self.config:
            self.file_input.setText(self.config["source_dir"])

        if "config_path" in self.config:
            self.config_path_input.setText(self.config["config_path"])
        
        if "backup_path" in self.config:
            self.backup_dir_input.setText(self.config["backup_path"])

        # Update document specific settings
        if "title" in self.config["document"]:
            self.title_input.setText(self.config["document"]["title"])
        if "version" in self.config["document"]:
            self.version_input.setText(self.config["document"]["version"])
        if "author" in self.config["document"]:
            self.author_input.setText(self.config["document"]["author"])
        if "date" in self.config["document"]:
            self.date_input.setText(self.config["document"]["date"])
        if "logoPath" in self.config["document"]:
            self.logo_path_input.setText(self.config["document"]["logoPath"])
        if "highlightTodo" in self.config["document"]:
            self.highlightToDo.setChecked(self.config["document"]["highlightTodo"])
            # Set config Changed again FALSE because it was no user interaction!
            self.configChanged = False
        if "showDocProgress" in self.config["document"]:
            self.showDocProgress.setChecked(self.config["document"]["showDocProgress"])
            self.configChanged = False

    def open_output_directory(self, path):
        output_path = ""

        if (path == "log"):
            output_path = loggingDirectory
        elif (path == "doc"):
            output_path = self.output_path_input.text()
        else:
            logger.log(f"{path} not supported!", "info")

        if output_path:
            dir_path = os.path.dirname(os.path.abspath(output_path))
            if os.path.exists(dir_path):
                if sys.platform == "win32":
                    subprocess.run(["explorer", dir_path])
                elif sys.platform == "darwin":
                    subprocess.run(["open", dir_path])
                else:
                    subprocess.run(["xdg-open", dir_path])
            else:
                self.append_log(f"⚠️ Output directory not found: {dir_path}")
        else:
            self.append_log("⚠️ Output path is empty.")

    def change_language(self, lang):
        # if language is changed, update the translator
        self.translator = self.Translator(lang=lang)
        # Update UI
        self.update_ui()

    def update_ui(self):
        # Updating UI Tabs Navigation Labels in Header Line
        self.tabs.setTabText(self.tabs.indexOf(self.start_tab), self.translator.translate("mainTabs.start"))
        self.tabs.setTabText(self.tabs.indexOf(self.settings_tab), self.translator.translate("mainTabs.settings"))
        self.tabs.setTabText(self.tabs.indexOf(self.log_tab), self.translator.translate("mainTabs.log"))
        self.tabs.setTabText(self.tabs.indexOf(self.about_tab), self.translator.translate("mainTabs.about"))
        self.tabs.setTabText(self.tabs.indexOf(self.help_tab), self.translator.translate("mainTabs.help"))
        self.tabs.setTabToolTip(self.tabs.indexOf(self.help_tab), self.translator.translate("mainTabs.helpToolTip"))

        # Updating Elements within "start" Tab
        self.config_path_input.setPlaceholderText(self.translator.translate("startTab.ConfigPathPlaceHolder"))
        self.file_input.setPlaceholderText(self.translator.translate("startTab.FileInputPlaceHolder"))
        self.select_configFile_button.setText(self.translator.translate("startTab.SelectConfigFileButton"))
        self.select_sourceFile_button.setText(self.translator.translate("startTab.SelectSourceFileButton"))
        self.select_sourceDir_button.setText(self.translator.translate("startTab.SelectSourceDirButton"))
        self.generate_button.setText(self.translator.translate("startTab.CreateDocButton"))
        self.status_label.setText(self.translator.translate("states.ready"))
        self.open_outputDoc_dir_button.setText(self.translator.translate("startTab.OpenOutputDirButton"))

        # Updating Elements within "settings" Tab
        self.lang_combo_label.setText(self.translator.translate("settingsTab.LangComboLabel"))
        # Updating Text in first group collection
        self.readonly_checkbox.setText(self.translator.translate("settingsTab.ReadOnlyCheckBox"))
        self.recursive_checkbox.setText(self.translator.translate("settingsTab.RecursiveCheckbox"))
        self.backup_dir_label.setText(self.translator.translate("settingsTab.BackupDirLabel"))
        self.backup_dir_input.setPlaceholderText(self.translator.translate("settingsTab.BackupDirPlaceHolder"))
        self.select_backupDir_button.setText(self.translator.translate("settingsTab.BackupDirButton"))
        self.general_expandable.setWidgetTitle(self.translator.translate("settingsTab.GeneralSettingsExpandable"))

        # Updating Text in second group collection
        self.highlightToDo.setText(self.translator.translate("settingsTab.HighlightToDoCheckbox"))
        self.showDocProgress.setText(self.translator.translate("settingsTab.showDocProgressCheckbox"))
        self.title_input.setPlaceholderText(self.translator.translate("settingsTab.titlePlaceHolder"))
        self.title_input_label.setText(self.translator.translate("settingsTab.titleLabel"))
        self.version_input.setPlaceholderText(self.translator.translate("settingsTab.docVersionPlaceHolder"))
        self.version_input_label.setText(self.translator.translate("settingsTab.docVersionLabel"))
        self.author_input.setPlaceholderText(self.translator.translate("settingsTab.docAuthorPlaceHolder"))
        self.author_input_label.setText(self.translator.translate("settingsTab.docAuthorLabel"))
        self.date_input.setPlaceholderText(self.translator.translate("settingsTab.docDatePlaceHolder"))
        self.date_input_label.setText(self.translator.translate("settingsTab.docDateLabel"))
        self.logo_path_input.setPlaceholderText(self.translator.translate("settingsTab.docLogoPlaceHolder"))
        self.logo_path_input_label.setText(self.translator.translate("settingsTab.docLogoLabel"))
        self.document_expandable.setWidgetTitle(self.translator.translate("settingsTab.DocSettingsExpandable"))

        # Update Text in third group collection
        self.output_format_input_label.setText(self.translator.translate("settingsTab.OutputFormatInputLabel"))
        self.output_format_input.setItemText(0, self.translator.translate("settingsTab.HMTLprefix"))
        self.output_format_input.setItemText(1, self.translator.translate("settingsTab.MDprefix"))
        self.output_format_input.setItemText(2, self.translator.translate("settingsTab.Allprefix"))

        self.header_comment_style_label.setText(self.translator.translate("settingsTab.HeaderCommentStyleLabel"))
        self.header_comment_style.setItemText(0, self.translator.translate("settingsTab.Doxygenprefix"))
        self.header_comment_style.setItemText(1, self.translator.translate("settingsTab.Defaultprefix"))

        self.output_path_input_label.setText(self.translator.translate("settingsTab.OutputPathInputLabel"))
        self.output_path_input.setPlaceholderText(self.translator.translate("settingsTab.OutputPathInputPlaceholder"))
        self.select_outputDir_button.setText(self.translator.translate("settingsTab.OutputDirButton"))
        
        self.output_expandable.setWidgetTitle(self.translator.translate("settingsTab.OutputSettingsExpandable"))

        # Updating Elements within "Logging"-Tab
        self.open_outputLog_dir_button.setText(self.translator.translate("loggingTab.OpenOutputLogDirButton"))

    def check_for_update(self):
        try:
            url = f"https://api.github.com/repos/{__GITHUB_REPO__}/releases/latest"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            latest_version = data["tag_name"].lstrip("v")

            if latest_version > __version__:
                box = QMessageBox()
                box.setIcon(QMessageBox.Information)
                box.setWindowTitle("Update Available")
                box.setWindowIcon(QIcon(self.icon_path))
                box.setText(
                    f"A newer version ({latest_version}) is available on GitHub!\n\n"
                    f"You're using {__version__}.\n\nVisit:\nhttps://github.com/{__GITHUB_REPO__}/releases",
                )
                box.exec()
            else:
                box = QMessageBox()
                box.setIcon(QMessageBox.Information)
                box.setWindowTitle("Up to Date")
                box.setWindowIcon(QIcon(self.icon_path))
                box.setText(
                    f"You are already using the latest version ({__version__})."
                )
                box.exec()

        except Exception as e:
                logger.log(f"Could not check for updates: {str(e)}", "warning")
                box = QMessageBox()
                box.setIcon(QMessageBox.Warning)
                box.setWindowTitle("Update Check Failed")
                box.setWindowIcon(QIcon(self.icon_path))
                box.setText(
                    f"Could not check for updates:\n{str(e)}"
                )
                box.exec()

    def updateConfigFromUserInput(self):
        # Check if config path has been changed
        config_path_file = self.config_path_input.text().strip()
        if os.path.isfile(config_path_file):
            self.config["config_path"] = config_path_file
        else:
            logger.log(f"Config Path is not valid or does not exist: {config_path_file}", "warning")
            self.config["config_path"] = ""

        # start with default overloaded file and then overwrite user input settings
        self.config, errors = load_config(self.config["config_path"])
        if errors:
            for err in errors:
                logger.log(f"Error while parsing/loading config file: {err}", "warning")
                box = QMessageBox()
                box.setIcon(QMessageBox.Warning)
                box.setWindowTitle("Update config file failed!")
                box.setWindowIcon(QIcon(self.icon_path))
                box.setText(
                    f"Error while parsing/loading config file: {err}"
                )
                box.exec()

        if not self.config:
            logger.log("No Config file found or path invalid!", "warning")
            self.status_label.setText('State: No Config File found or path invalid!')
            return

        # Override Configuration Settings with (optional available) GUI-Values
        if self.output_format_input.currentText():
            # List, optional later to add more output formats like pdf
            formats = [fmt.strip() for fmt in self.output_format_input.currentText().split(",")]
            if self.translator.translate("settingsTab.Allprefix") in formats:
                self.config["output_format"] = ["html", "md"]
            else:
                self.config["output_format"] = formats

        if self.header_comment_style.currentText():
            self.config["headerCommentStyle"] = self.header_comment_style.currentText().strip()

        output_path_input = self.output_path_input.text().strip()
        if output_path_input:
            if(check_input_string_looks_like_path(output_path_input)):
                self.config["output_path"] = output_path_input
            else:
                logger.log(f"Output Path is not valid - abort: {output_path_input}", "warning")
                self.status_label.setText(f"ERROR: Invalid Output Path: '{output_path_input}'")
                return
            
        if self.file_input.text():
            self.config["source_dir"] = self.file_input.text()

        # Set Backup path none if "no-value" was entered on gui!
        backup_dir = self.backup_dir_input.text().strip()
        if backup_dir:
            self.config["backup_path"] = backup_dir
        else:
            self.config["backup_path"] = None
        
        # Override Document Settings with (optional available) GUI-Values
        if self.title_input.text():
            self.config["document"]["title"] = self.title_input.text()

        if self.version_input.text():
            self.config["document"]["version"] = self.version_input.text()

        if self.author_input.text():
            self.config["document"]["author"] = self.author_input.text()

        if self.date_input.text():
            self.config["document"]["date"] = self.date_input.text()

        logo_file_path = self.logo_path_input.text().strip()
        if logo_file_path:
            if os.path.isfile(logo_file_path):
                self.config["document"]["logoPath"] = logo_file_path
            else:
                logger.log(f"Logo Path can't be found: {logo_file_path}", "warning")
                self.config["document"]["logoPath"] = None

        if self.configChanged:
            # Check general settings if there has been something changed
            # Check "Readonly" Checkbox
            if self.readonly_checkbox.isChecked():
                self.config["readonly"] = True
            else:
                self.config["readonly"] = False

            # Check "Recursive"- Source dir checkbox
            if self.recursive_checkbox.isChecked():
                self.config["recursive"] = True
            else:
                self.config["recursive"] = False

            # Check document specific settings if there hase been something changed
            # Check Highlight ToDo if checked
            if self.highlightToDo.isChecked():
                self.config["document"]["highlightTodo"] = True
            else:
                self.config["document"]["highlightTodo"] = False
            
            # Check Show Progress if checked
            if self.showDocProgress.isChecked():
                self.config["document"]["showDocProgress"] = True
            else:
                self.config["document"]["showDocProgress"] = False

    def generate_documentation(self):
        logger.log("Start Documentation", "info")
        self.open_outputDoc_dir_button.setVisible(False)
        self.status_label.setText('State: Generating Documentation...')

        self.updateConfigFromUserInput()

        # Input Data
        source_files = ""
        source_file = self.file_input.text() if self.file_input.text() else None
        if source_file:
            if os.path.isfile(source_file):
                #check if it is a file
                source_files = [source_file]
            elif os.path.isdir(source_file):
                #else check if it is a directory
                source_files = get_cpp_files(source_file, self.config)
            else:
                logger.log(f"Input file is whether file or directory: {source_file}", "warning")
        else:
            source_files = get_cpp_files(self.config["source_dir"], self.config)
            logger.log(f"Using Doc. Source form config-File: {source_file}", "info")
        
        if source_files:
            # Generate Documentation
            all_functions = generate_documentation(self.config, source_files)

            if isinstance(all_functions, str) and all_functions.startswith("ERROR"):
                logger.log(f"Documentation was not created successfull: {all_functions}", "warning")
                self.status_label.setText(f"{all_functions}")
                return

            # Save Documentation to File
            if len(all_functions) != 0:
                try:
                    result_files, stats = save_documentation(self.config, all_functions)
                    if result_files:
                        self.status_label.setText(f'STATE: {stats["percent_done"]}% of Documentation created successfull!')
                        self.open_outputDoc_dir_button.setVisible(True)
                        logger.log(f"Documentation created successfull at {result_files}", "info")
                        return stats["percent_done"]
                    else:
                        self.status_label.setText("STATE: Documentation was not created successfull!")
                        logger.log("Documentation was not created successfull!", "warning")
                except ValueError as e:
                    logger.log(f"Invalid Report Output Format: '{str(e)}'", "error")
                    self.status_label.setText(f"ERROR: Invalid Report Output Format: '{str(e)}'")
                except Exception as e:
                    logger.log(f"Unexpected Behaviour: '{str(e)}'", "error")
                    self.status_label.setText(f"ERROR: Unexpected Behaviour: '{str(e)}'")
            else:
                logger.log("No Functions to Document found", "info")
                self.status_label.setText("STATE: No Functions to Document found")
        else:
            logger.log("no source files found or not valid!", "warning")
            self.status_label.setText("STATE: Source file is neither file nor directory!")

# ========================== CLI PART ==========================
def print_license():
    SEPERATOR_LINE = "============================================================================"
    print(SEPERATOR_LINE)
    print(__license_text__)
    print(SEPERATOR_LINE)

def print_intro_message():
    SEPERATOR_LINE = "============================================================================"
    print(SEPERATOR_LINE)
    print(f"{__title__} v{__version__}")
    print(f"{__license_header__}")
    print("This program comes with ABSOLUTELY NO WARRANTY; for details type `--license`.")
    print(SEPERATOR_LINE)

def run_cli_mode(args):

    logger.log("CLI Mode started", "info")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_config_path = os.path.join(script_dir, 'config.yaml')

    config, errors = load_config(args.config if args.config else default_config_path)
    config["app_info"] = {
        "version": __version__,
        "title": __title__,
        "description": __description__,
        "author": __author__
    }
    if errors:
        for err in errors:
            logger.log(f"Error while parsing/loading config file: {err}", "warning")
    source_files = get_files(args, config)
    all_functions = generate_documentation(config, source_files)

    if len(all_functions) != 0:
        try:
            result_files, stats = save_documentation(config, all_functions)
            if result_files:
                logger.log(f"Documentation created successfull at {result_files}", "info")
                return stats["percent_done"]
            else:
                logger.log("Documentation was not created successfull!", "warning")
        except ValueError as e:
            logger.log(f"Invalid Report Output Format: '{str(e)}'", "Error")
        except Exception as e:
            logger.log(f"Unexpected Behaviour: '{str(e)}'", "Error")
    else:
        logger.log("No Functions to Document found", "info")

# ========================== ENTRY POINT ==========================
def main():

    print_intro_message()

    parser = argparse.ArgumentParser(description=f"{__description__} (GUI or CLI)")
    parser.add_argument("--license", action="store_true", help="show full license information")
    parser.add_argument("--NoGui", action="store_true", help="Launch with GUI instead of CLI")
    parser.add_argument("--file", help="Optional: specific source file")
    parser.add_argument("--config", help="Optional: path to custom config file")
    
    args, unknown = parser.parse_known_args()

    # Logging SW-Version and optional input arguments to log-file
    logger.log(f"{__title__} {__version__} by {__author__}", "info")
    logger.log(f"Input arguments: {args}", "info")

    # Starting own-ended config files, means overloading only filepath to Program.
    # with this for loop, this kind of config files can be selected
    for item in unknown:
        if item.lower().endswith(f"{__file_extension__}") and not args.config:
            logger.log(f"Treating {__file_extension__} file '{item}' as config file.", "info")
            args.config = item
            unknown.remove(item)
            break

    if args.license:
        # Show license only in CLI if --license is selected
        print_license()
        return

    if unknown:
        logger.log(f"Unknown Input Arguments: {unknown}", "warning")

    if args.NoGui:
        total_done = run_cli_mode(args)
        print(f'Total Documentation done: {total_done}%')
        if(total_done < 99):
            sys.exit(total_done)
    else:
        app = QApplication(sys.argv)  
        window = DocGeneratorApp(config_path = args.config)
        window.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()
