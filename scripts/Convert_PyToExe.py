# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

"""
automatically creation of installer application by:
creting an .iss based file, compiling it to an .exe file
"""

import sys
import os
import re
import subprocess

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import findImports

from collections import defaultdict

from src.utils.app_info import (__title__, __version__, __file_extension__,
    __author__, __description__, __year__, __GITHUB_URL__,
    gpl_v3_full_text, __license_text__
)

def create_inno_setup_script(exe_name, app_title, app_version,
                             app_author, app_date, app_file_identifier):
    """
    Creation of Inno Setup Script (.iss) to create a Installer for the application.
    """
    script_content = f"""
#define AppName "{app_title}"
#define AppVersion "{app_version}"
#define AppExeName "{exe_name}"
#define AppExeNameWithIndex "{exe_name}.exe"
#define AppFileIdentifier "{app_file_identifier}"

[Setup]
AppId={{#AppName}}
AppName={{#AppName}}
AppVersion={{#AppVersion}}
AppPublisher="{app_author}"
AppComments="{__description__}"
AppSupportURL="{__GITHUB_URL__}"
DefaultDirName={{autopf}}\\{{#AppName}}
DefaultGroupName={{#AppName}}
OutputDir=.\\Installer
OutputBaseFilename={{#AppExeName}}_{{#AppVersion}}_Installer
Compression=lzma
SolidCompression=yes
DisableProgramGroupPage=yes
AlwaysShowDirOnReadyPage=yes
UninstallDisplayName={{#AppName}}
UninstallDisplayIcon={{app}}\\{{#AppExeNameWithIndex}}
LicenseFile={{#AppName}}\\_internal\\assets\\LICENSE\\LICENSE.txt
VersionInfoProductVersion={{#AppVersion}}
VersionInfoVersion={{#AppVersion}}
VersionInfoCopyright="@ {app_author} {app_date}"
VersionInfoCompany="{app_author}"

[Files]
Source: "{{#AppName}}\\*"; DestDir: "{{app}}\\"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{commondesktop}}\\{{#AppName}}"; Filename: "{{app}}\\{{#AppName}}.exe"
Name: "{{group}}\\{{#AppName}}"; Filename: "{{app}}\\{{#AppName}}.exe"

[Registry]
; Mapping extension key ".cppdoc" to App-File-Identifier
Root: HKCR; Subkey: ".{{#AppFileIdentifier}}"; ValueType: string; ValueName: ""; ValueData: "{{#AppName}}File"; Flags: uninsdeletevalue

; Definition of App-File-Identifier
Root: HKCR; Subkey: "{{#AppName}}File"; ValueType: string; ValueName: ""; ValueData: "{{#AppName}}File"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "{{#AppName}}File\\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{{app}}\\_internal\\assets\\FileExtension.ico"
Root: HKCR; Subkey: "{{#AppName}}File\\shell\\open\\command"; ValueType: string; ValueName: ""; ValueData: "\"\"{{app}}\\{{#AppExeNameWithIndex}}\"\" --config \"\"%1\"\""

; contextmenu - "open with CppCodeDoc"
Root: HKCR; Subkey: "{{#AppName}}File\\shell\\open"; ValueType: string; ValueName: "MUIVerb"; ValueData: "Open with {{#AppName}}"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "{{#AppName}}File\\shell\\open\\command"; ValueType: string; ValueName: ""; ValueData: "\"\"{{app}}\{{#AppExeNameWithIndex}}\"\" --config \"\"%1\"\""

[Run]
Filename: "{{app}}\\{{#AppName}}.exe"; Description: "Start {{#AppName}}"; Flags: nowait postinstall skipifsilent

; Setup Icon-Cache to avoid system restart
; Running on x64 Bit systems
Filename: "{{sysnative}}\\ie4uinit.exe"; Parameters: "-ClearIconCache"; StatusMsg: "Clearing Icon-Cache..."; Flags: runhidden; Check: IsWin64
Filename: "{{sysnative}}\\ie4uinit.exe"; Parameters: "-show"; StatusMsg: "Refreshing Explorer-Icons..."; Flags: runhidden; Check: IsWin64
; Running on x32 Bit systems
Filename: "{{sys}}\\ie4uinit.exe"; Parameters: "-ClearIconCache"; StatusMsg: "Clearing Icon-Cache..."; Flags: runhidden; Check: not IsWin64
Filename: "{{sys}}\\ie4uinit.exe"; Parameters: "-show"; StatusMsg: "Refreshing Explorer-Icons..."; Flags: runhidden; Check: not IsWin64
"""

    # Saving of .iss file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    inno_script_path = os.path.join(base_dir, "..", f"{exe_name}_Installer.iss")
    with open(inno_script_path, "w") as script_file:
        script_file.write(script_content)

    return inno_script_path

def create_version_file(exe_name, app_title, app_version, app_description, app_date, author):
    """
    Creation of version-file information for the application, generated by PyInstaller.
    This file is used to provide version information for the created .exe file.
    """
    # Ensuering, version consits of three parts (e.g. 1.0.0)
    version_parts = app_version.split(".")
    while len(version_parts) < 3:
        version_parts.append("0")
    version_str = ",".join(version_parts[:3]) + ",0"

    content = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_str}),
    prodvers=({version_str}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [
          StringStruct('CompanyName', '{author}'),
          StringStruct('LegalCopyright', f'© {author} {app_date}'),
          StringStruct('FileDescription', '{app_description}'),
          StringStruct('FileVersion', '{app_version}'),
          StringStruct('InternalName', '{exe_name}'),
          StringStruct('OriginalFilename', '{exe_name}.exe'),
          StringStruct('ProductName', '{app_title}'),
          StringStruct('ProductVersion', '{app_version}'),
          StringStruct('BuildDate', '{app_date}')
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""

    # determining saving location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    version_file_path = os.path.join(base_dir, "version_info.txt")

    # writing file
    with open(version_file_path, "w", encoding="utf-8") as f:
        f.write(content.strip())

    return version_file_path

def get_latest_tag():
    """"
    getting the latest git tag in the current repository.
    If no tags are available, it returns None.
    """
    try:
        tag = subprocess.check_output(
            ['git', 'describe', '--tags', '--abbrev=0'], shell=False
        ).decode().strip()
        return tag
    except subprocess.CalledProcessError:
        return None  # No tags available till now

def generate_changelog(new_version):
    """"
    function to generate a changelog based on the latest git commits.
    It groups commits by type and formats them into a markdown changelog section.
    """
    last_tag = get_latest_tag()
    print(f"Last Tag: {last_tag}")

    range_spec = f"{last_tag}..HEAD" if last_tag else "HEAD"

    # ✅ safety check - range_spec input validation for subprocess.run()
    if not re.fullmatch(r'[\w.\-/]+(\.\.HEAD)?', range_spec):
        raise ValueError(f"Unsafe range_spec detected: {range_spec}\n"
                         "Shell-injection risk! This error is raised to protect subprocess.run().")

    try:
        # getting GIT-COMMITS
        result = subprocess.run(
            ['git', 'log', range_spec, '--pretty=format:%s'],
            capture_output=True, text=True, check=True
        )
        all_commits = result.stdout.strip().split('\n')

        # grouping GIT-COMMITS by type
        commit_groups = defaultdict(list)
        valid_prefixes = ('feat:', 'fix:', 'docs:', 'refactor:', 'test:', 'chore:')

        for msg in all_commits:
            for prefix in valid_prefixes:
                if msg.startswith(prefix):
                    commit_type = prefix[:-1]
                    description = msg[len(prefix):].strip()
                    commit_groups[commit_type].append(description)
                    break

        # If there are no GROUPED COMMITS, break
        if not any(commit_groups.values()):
            print(f"⚠️ Keine changelog-relevanten Commits seit Tag {last_tag}.")
            return ""

        # Creating new Changelog Block
        changelog_lines = []
        order = ['feat', 'fix', 'docs', 'refactor', 'test', 'chore']
        type_titles = {
            'feat': 'Features',
            'fix': 'Bug Fixes',
            'docs': 'Documentation',
            'refactor': 'Refactoring',
            'test': 'Tests',
            'chore': 'Chores'
        }

        for ctype in order:
            if commit_groups[ctype]:
                changelog_lines.append(f"## {type_titles[ctype]}")
                changelog_lines.append("")  # Spacing Line after Header
                for desc in commit_groups[ctype]:
                    changelog_lines.append(f"* {desc}")
                changelog_lines.append("")

        new_body = "\n".join(changelog_lines).strip()
        new_section = f"# Changelog for version {new_version}\n\n{new_body}\n"

        changelog_path = "changelog.md"
        if os.path.exists(changelog_path):
            with open(changelog_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = ""

        # Check if block already exists in changelog
        version_pattern = re.compile(
            rf"(# Changelog for version {re.escape(new_version)}\n(?:.*?\n)*?)(?=^# Changelog for version |\Z)",
            re.MULTILINE
        )
        match = version_pattern.search(content)

        def normalize(text):
            """"
            simple normalization function to remove leading/trailing spaces and empty lines.
            """
            return "\n".join(line.strip() for line in text.strip().splitlines())

        if match:
            existing_block = match.group(1)
            # skip 2 header lines
            existing_body = normalize("\n".join(existing_block.splitlines()[2:]))
            new_body_normalized = normalize(new_body)

            if new_body_normalized in existing_body:
                print(f"🔁 Changelog for Version {new_version} already exists and is up-to-date.")
                return new_section

            # appending version block if it does not already exist
            combined_body = existing_body + "\n" + new_body_normalized
            combined_section = f"# Changelog for version {new_version}\n\n{combined_body.strip()}\n"

            content = version_pattern.sub(combined_section + "\n", content)
            print(f"🔁 Changelog-Entry for Version {new_version} appended.")
        else:
            # Adding new block on top of the changelog
            content = new_section + "\n" + content
            print(f"🆕 New Changelog-Entry for version {new_version} added.")

        with open(changelog_path, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")

        return new_section

    except subprocess.CalledProcessError as e:
        print(f"Error while creating the changelog: {e}")
        return ""

def convert_license_file():
    """"
    Convertion of license file, based on App-informations
    """
    with open("LICENSE.txt", "w", encoding="utf-8") as f:
        f.write(__license_text__.strip())
        f.write("\n\n")
        f.write(gpl_v3_full_text.strip())

def compile_inno_setup_script(iss_path):
    """"
    Compiling the Inno Setup script (.iss) to create the installer.
    """
    try:
        iscc_exe = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

        if not os.path.isfile(iss_path):
            raise FileNotFoundError(f"The .iss-File can not be found: {iss_path}")
        
        if not iss_path.lower().endswith('.iss') or not re.fullmatch(r'[\w\s\-\./:\\]+', iss_path):
            raise ValueError(f"Unsafe iss_path detected: {iss_path}")

        if not iss_path.lower().endswith('.iss') or not re.fullmatch(r'[\w\s\-\./:\\]+', iss_path):
            raise ValueError(f"Unsafe iss_path detected: {iss_path}")

        # start subprocess to run Inno Setup Compiler and log output in terminal
        process = subprocess.Popen(
            [iscc_exe, iss_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Call output line by line
        for line in process.stdout:
            print(line, end='')  # 'end' line already has \n so end is ''

        process.stdout.close()
        return_code = process.wait()

        if return_code != 0:
            print(f"ISCC.exe exited with code {return_code}")
        else:
            print("Compiling successfully!")

    except FileNotFoundError as e:
        print(f"FileError: {e}")
    except Exception as e:
        print(f"Unkown Error: {e}")


def run_pylint_analysis(source_dir="./src", json_output="pylint-output.json",
                        html_output="pylint-report.html", fail_under_score=None):
    """
    Checking code-quality by runnint pylint-code-analysis and
    generating a report in html/json file out of src directory.
    Build is canceling if pylint returns an error, or score is below fial_under_score!
    """
    print("🔍 Running pylint analysis...")

    # exit codes
    pylint_exit_messages = {
        0:  "✅ No issues found.",
        1:  "❌ Fatal message issued.",
        2:  "❌ Error message issued.",
        4:  "⚠️ Warning message issued.",
        8:  "ℹ️ Refactor message issued.",
        16: "ℹ️ Convention message issued.",
        30: "❌ Score below threshold (--fail-under).",
        32: "❌ Usage error.",
        64: "❌ Internal pylint error.",
    }

    # Step 1: call pylint with JSON - output with fail-under if set
    try:
        args = ["pylint", source_dir, "--output-format=json"]
        if fail_under_score is not None:
            args.append(f"--fail-under={fail_under_score}")

        with open(json_output, "w", encoding="utf-8") as out_file:
            result = subprocess.run(
                args,
                stdout=out_file,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )

        exit_code = result.returncode
        message = pylint_exit_messages.get(exit_code, f"⚠️ Unknown exit code: {exit_code}")
        print(f"📄 Pylint finished with exit code {exit_code}: \"{message}\"")

        if exit_code not in (0, 4, 8, 16):
            sys.exit(exit_code)
        else:
            print(f"✅ pylint JSON output created: {json_output}")

    except Exception as e:
        print(f"❌ Unexpected error during pylint execution: {e}")
        sys.exit(1)

    # Step 2: JSON → HTML
    try:
        subprocess.run(
            ["pylint-json2html", "-f", "json", json_output, "-o", html_output],
            check=True,
            shell=False
        )
        print(f"✅ HTML report saved as '{html_output}'")

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create HTML report: {e}")
        sys.exit(1)


def convert_to_exe(script_path):
    """
    Convertion of a python based application to a executable (.exe) file using PyInstaller.
    """
    try:
        from src.configSetup.installModules import ensure_modules
        ensure_modules([("PyInstaller", "pyinstaller"),
                        ("pylint", "pylint"),
                        ("","pylint-json2html")])
        import PyInstaller
    except ImportError:
        print("PyInstaller is not installed. install it by using 'pip install pyinstaller'.")
        sys.exit(1)

    # ensure, file exists
    if not os.path.isfile(script_path):
        print(f"The file  '{script_path}' does not exist.")
        sys.exit(1)

    exe_name = f"{__title__}"

    # Create License file
    convert_license_file()

    # Create Version Information for creted .exe file
    version_file_path = create_version_file(exe_name, __title__, __version__, __description__, __year__, __author__)

    # PyInstaller command built
    command = [
        "pyinstaller",
        "-y",                                                               # Remove Output direcotry without confirmation - ensure build always start from clean conditions!
        "--onedir",                                                         # Create one direcotry
        "--clean",                                                          # Cleanup last Builds
        "--log-level", "DEBUG",                                             # Log-Level set to  DEBUG for detail information
        "--name", exe_name,
        "--icon", r".\src\utils\icon\icon.ico",
        "--version-file", version_file_path,
        "--paths", "./src",                                                 # Projectpath is within ./src folder and not within parrent folder!
        "--add-data", r"LICENSE.txt;assets\LICENSE",                        #
        "--add-data", r"help.md;assets",                                    #
        "--add-data", r"changelog.md;assets",                               #
        "--add-data", r".\src\lang;assets\lang",                            #
        "--add-data", r".\src\fileExamples\testFile.h;assets\fileExamples", #
        "--add-data", r".\src\config.yaml;assets",
        "--add-data", r".\src\generator\img\logo.svg;assets",
        "--add-data", r".\src\generator\img\Ko-fi.svg;assets",
        "--add-data", r".\src\generator\img\paypal.svg;assets",
        "--add-data", r".\src\generator\img\github.svg;assets",
        "--add-data", r".\src\generator\img\DarkMode.svg;assets",
        "--add-data", r".\src\utils\icon\icon.ico;assets",
        "--add-data", r".\src\utils\icon\FileExtension.ico;assets",
        "--add-data", r".\src\generator\img\Reference.png;assets",
        "--distpath", r".",                                                 # Distribution path is in parrent-dir .\CppCodeDoc folder!
        "--uac-admin",
        "--windowed",                                                       # Calling GUI-only without Console-Terminal
        script_path                                                         # Path to python main file
    ]

    print("Start .py to .exe conversion...")

    # calling PyInstaller within subprocess with output monitoring in terminal
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             shell=False)
    print(process.stdout.decode())
    print(process.stderr.decode())

    # Check if compiling was successfull
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(base_dir, "..", "CppCodeDoc")
    exe_path = os.path.join(dist_dir, f"{exe_name}.exe")

    if os.path.isfile(exe_path):
        print(f".exe-file created successfull at: {exe_path}")
        print("⚠️⚠️⚠️⚠️⚠️----------⚠️⚠️⚠️⚠️⚠️----------⚠️⚠️⚠️⚠️⚠️\n")
        print("--❌------ DO NOT FORGET TO CREATE THE INSTALLER ------❌--\n")
        print("⚠️⚠️⚠️⚠️⚠️----------⚠️⚠️⚠️⚠️⚠️----------⚠️⚠️⚠️⚠️⚠️")
    else:
        print(f"Error during creation of .exe file in {exe_path}. Check previous log outputs!")
        return

    # Creating Inno Setup-Script and compile installer
    inno_script_path = (
        create_inno_setup_script(exe_name, __title__, __version__,
                                  __author__, __year__, __file_extension__.lstrip('.'))
        )
    print(f"Installer script created at: {inno_script_path}")
    compile_inno_setup_script(inno_script_path)

    # Checking code quality with pylint
    run_pylint_analysis(source_dir="./src", json_output="src_output.json",
                        html_output="src_report.html", fail_under_score=5.0)
    run_pylint_analysis(source_dir="./test", json_output="test_output.json",
                    html_output="test_report.html", fail_under_score=5.0)
    run_pylint_analysis(source_dir="./scripts", json_output="scripts_output.json",
                    html_output="scripts_report.html", fail_under_score=5.0)

if __name__ == "__main__":


    # Update/Recreate the list of imports
    findImports.main()

    # updating changelog file
    generate_changelog(__version__)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    script_to_convert = os.path.join(project_root, "src", "CppCodeDoc.py")

    convert_to_exe(script_to_convert)
