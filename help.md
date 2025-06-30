# Help & Documentation of CPPCodeDoc

This Document fungates as Help if information about software functionality is needed.

If any information is missing or you need further assistance, don’t hesitate to contact the development team on GitHub by submitting an issue or joining a discussion.

Link [![Github][github-shield]][github-url]

---

## 📚 Table of Content
- [Interaction by GUI](#interaction-by-gui)
- [Interaction by CLI](#interaction-by-cli)
- [Start Tab](#start-tab)
    - [Enter Config Path](#enter-config-path)
    - [Select Configuration File](#select-config-file)
    - [Save Configuration File](#save-config-file)
    - [Enter Source File or Directory](#enter-file-source)
    - [Select Source File](#select-source-file)
    - [Select Source Directory](#select-source-dir)
    - [Generate Documentation](#generate-doc)
    - [Status Display](#status-display)
    - [Open Output Directory](#open-output-dir)
- [Settings Tab](#settings-tab)
    - [General Settings](#general-settings)
    - [Document Settings](#document-settings)
    - [Output Settings](#output-settings)
- [Logging Tab](#logging-tab)
- [About Tab](#about-tab)

<a id="interaction-by-gui"></a>

## 💬 Interaction by GUI

Use the application GUI to interactively configure paths, select source files or directories, and generate documentation based on your C++ source code.

- **Toggle Dark/Light Mode** The global UI includes a toggle control to switch between light and dark mode.

- **Sponsorship** In the bottom right, you’ll find sponsorship information for PayPal, Ko-fi, and a GitHub link. Clicking on any of these opens the respective URL in your browser.

- **Navigation tab** within the navigation tab you can switch between start, settings, log, about and help. See description below for more detailed information about each tab.

<a id="interaction-by-cli"></a>

## 💬 Interaction by CLI

The application can also be used by the command line by calling it with python:

```bash
python .\CppCodeDoc.py --NoGui
```

It starts then automatically generating the Documentation based on the default config file. For a custom config file, you can also use the config specific overload paramter like:

```bash
python .\CppCodeDoc.py --NoGui --config .\myConfigFile.cppdoc
```

There is also the possibility to use it directly with one specific file for code documentation:

```bash
python .\CppCodeDoc.py --NoGui --file .\myProject.ino
```

Furthermore, the CLI based function returns the total commend-covergae percentage value of the documentation. This can be further used e.g. for CI/CD purpose to ensure that commited code meets a minimum level of commenting coverage at all bevor commiting into final repo. 

To know more about the application, you can also use the ´--license´ information or the ´--help´ tag to see more within the CMD window.


---
<a id="start-tab"></a>

### 🏁 Start Tab

Entry point of the UI. The UI starts per default with a standard configuration meeting the testing environment during developement. The standard language is English and the light-mode is used.

<a id="enter-config-path"></a>

-  **Enter Config Path** At the top of the Start Tab, you can manually enter the path to a `.yaml` based configuration file in `.cppDoc` format. This path determines how the documentation process behaves. Any change to this field triggers a configuration update internally.

<a id="select-config-file"></a>

- **Select Configuration File** Click the **“Select Config File”** button to open a file dialog and choose a YAML-based ´.cppDoc´ configuration file. This allows you to skip manual path input and select the correct file easily.

<a id="save-config-file"></a>

- **Save Configuration File** Click the **“Save Config File”** button to save the current configuration settings into a `.cppDoc` file. This is useful after modifying any field values to persist the current setup.

<a id="enter-file-source"></a>

- **Enter Source File or Directory** This text input lets you specify the file or folder to be documented. You can type the path manually or populate it via the source selection buttons below.

<a id="select-source-file"></a>

- **Select Source File** Click the **“Select Source File”** button to choose a single C++ source file for documentation. The selected file path is automatically inserted into the input field.

<a id="select-source-dir"></a>

- **Select Source Directory** Click the **“Select Source Directory”** button to choose a folder containing multiple C++ files. This is useful when documenting a complete project. In Settings tab you can also activate the "Recursive" function to iterate through all sub-directorys or even not.

<a id="generate-doc"></a>

- **Generate Documentation** Click the **“Generate Documentation”** button to start the documentation process. This uses the selected files and configuration to create structured, browsable documentation (e.g., via Doxygen).

<a id="status-display"></a>

- **Status Display** Below the main buttons is a **status label** that shows the current state of the application, such as “Ready,” “Generating…,” or error messages during processing.

<a id="open-output-dir"></a>

- **Open Output Directory** Once documentation has been generated successfully, the **“Open Output Directory”** button becomes visible. Click it to open the folder where the generated documentation was saved.

---

<a id="settings-tab"></a>

## ⚙️ Settings Tab

Use this tab to configure how documentation is generated and formatted. All settings are divided into three expandable sections:

- **Language Selection** Choose between English and German for the UI language via a dropdown.

---

<a id="general-settings"></a>

### 🔧 General Settings

- **Read-Only Mode** Enables a read-only mode to prevent overwriting source files.

- **Recursive Parsing** When checked, the application will recursively scan all subdirectories for source files.

- **Enter Backup Directory** Input a folder where backups of modified files will be stored before overwriting. This is optional but recommended for safety.

- **Select Backup Directory** Interactive selection of Backup Directory input via filebrowser navigation. Selected directory is updating the enter backup directory field.

---

<a id="document-settings"></a>

### 📝 Document Settings

- **Highlight TODO Comments** Enables highlighting of `TODO:` Tags within the final documentation report and similar tags in the generated documentation.

- **Show Documentation Progress** Displays a summary of documented vs. undocumented code items in percentage.

- **Document Title** Title text to appear at the top of the generated documentation.

- **Document Version** The version string of the documentation (e.g., `v1.0.3`).

- **Author Name** Specifies the name of the documentation author.

- **Documentation Date** Free text input for the documentation date (e.g., today's date or release date).

- **Logo Path** Optional path to a projectspecific logo image that will be embedded in the generated documentation (if supported by format).

---

<a id="output-settings"></a>

### 🧾 Output Settings

- **Output Format** Select between `HTML`, `Markdown (.md)` or `All` for the format of the documentation.

- **Comment Style** Choose the style of comment headers, modified in the sourcefiles:
  - `Doxygen` – use `/** ... */` format.
  - `Default` – plain inline comments.

    (important: setting only works if readonly is disabled)

- **Enter Output Path** Input the directory where the generated documentation will be saved.

- **Select Output Path** Select the directory where the generated documentation will be saved via filebrowser. If input was successfull, the OutputPath Input filed will be updated

---

<a id="logging-tab"></a>

## 📜 Logging Tab

This tab provides a simple interface for viewing log output directly within the application.

- **Log Output Display** Shows the live log messages in a scrollable widget.

- **Open Log Output Directory Button** Opens the directory where log files are saved, so you can quickly access log files for review or troubleshooting.

---

<a id="about-tab"></a>

## ℹ️ About Tab

This tab provides general information about the software and its authorship.

- **Software Title and Version** Displays the software name and the current version number.

- **Author** Shows the author's name.

- **Repository Link** Provides a clickable hyperlink to the project’s GitHub repository for easy access to the source code and issues.

- **Description** A read-only text area with a detailed description of the software.

- **Check for Update Button** A button to manually trigger a check for available software updates.

- **License Information** Displays the full license text in a scrollable read-only area.

---

[github-shield]: https://img.shields.io/badge/GitHub-Jojos1220-black?logo=github
[github-url]: https://github.com/JoJos1220/CppCodeDoc
