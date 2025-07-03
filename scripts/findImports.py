# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

"""
file is searching on all modules/packages import and
writes the information summarized into a requirements.txt file.
"""

import ast
import sys
import os
import importlib.metadata
from pathlib import Path
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.app_info import (__license_header__)

from src.configSetup.installModules import ensure_modules
ensure_modules([("stdlib_list", "stdlib_list")])
import stdlib_list

# 📦 Mapping: known module names/pip-package names
KNOWN_PKG_MAP = {
    "yaml": "PyYAML",
}


def get_stdlib_modules():
    """
    getting all stdlib modules
    """
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    return set(stdlib_list.stdlib_list(version))


def find_python_files(root: Path):
    """
    returning all python files in folder
    """
    return list(root.rglob("*.py"))


def find_local_modules(py_files, root: Path):
    """
    searching on local modules in folder.
    """
    local = set()
    for path in py_files:
        rel = path.relative_to(root)
        name = rel.parts[0]
        if name != "__pycache__":
            local.add(name)
    return local


def extract_imports(py_files):
    """
    extracting all imports out of src files.
    """
    imports = set()
    for file_path in py_files:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=str(file_path))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            imports.add(n.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports.add(node.module.split('.')[0])
            except Exception as e:
                print(f"⚠ Error during parsing of {file_path}: {e}")
    return imports


def resolve_modules(imports, stdlib, local_modules):
    """
    resolving modules on network by name.
    """
    external = sorted(
        mod for mod in imports
        if mod not in stdlib and mod not in local_modules
    )

    found, not_found = [], []

    for mod in external:
        try:
            dist = importlib.metadata.distribution(mod)
            found.append((mod, dist.metadata["Name"]))
        except importlib.metadata.PackageNotFoundError:
            pkg = KNOWN_PKG_MAP.get(mod)
            if pkg:
                found.append((mod, pkg))
            else:
                not_found.append(mod)

    return found, not_found


def write_requirements_txt(packages):
    """
    writing all packages, found to requirements.txt file.
    if alrady exist, file will be updated.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def get_package_version(pkg_name):
        try:
            return importlib.metadata.version(pkg_name)
        except importlib.metadata.PackageNotFoundError:
            return None

    def get_license(pkg_name):
        try:
            meta = importlib.metadata.metadata(pkg_name)
            return meta.get("License", "Unknown")
        except importlib.metadata.PackageNotFoundError:
            return "Unknown"

    with open("requirements.txt", "w", encoding="utf-8") as f:

        # Project-Metadata
        f.write(f"{__license_header__}\n\n")

        f.write(f"# requirements.txt generated: {timestamp}\n\n")
        for _, pkg in packages:
            version = get_package_version(pkg)
            license_info = get_license(pkg)
            f.write(f"# Third-Party Package name/License: {pkg}: {license_info}\n")
            if version:
                f.write(f"{pkg}=={version}\n")
            else:
                f.write(f"{pkg}\n")


def print_summary(found, not_found):
    """
    printing sumary of found modules into console.
    """
    print("\n✅ found external modules (via ensure_modules):\n")
    print("ensure_modules([")
    for mod, pkg in found:
        print(f'    ("{mod}", "{pkg}"),')
    print("])")

    if not_found:
        print("\n⚠ Not automatic resolveable – please check manually:")
        for mod in not_found:
            print(f"- {mod}")

def print_licenses(packages):
    """
    printing package license out of each imported modul.
    """
    print("📄 Licenseinformationen to the found Packages:\n")
    for _, pkg_name in packages:
        try:
            meta = importlib.metadata.metadata(pkg_name)
            license_info = meta.get("License", "Unbekannt")
            print(f"{pkg_name}: {license_info}")
        except importlib.metadata.PackageNotFoundError:
            print(f"{pkg_name}: ❌ Package not found")
    print("")

def main():
    """
    Main function to find imports
    """
    root = Path(".").resolve()
    stdlib = get_stdlib_modules()
    py_files = find_python_files(root)
    local_modules = find_local_modules(py_files, root)
    used_modules = extract_imports(py_files)
    found, not_found = resolve_modules(used_modules, stdlib, local_modules)
    print_summary(found, not_found)
    write_requirements_txt(found)
    print("\n📦 requirements.txt successfully created!")
    print_licenses(found)


if __name__ == "__main__":
    main()
