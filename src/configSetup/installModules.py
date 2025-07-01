# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys
import importlib
import subprocess

def ensure_modules(modules):
    """
    modules: list of datatype tuple (import_name, pip_name)
             e.g. [("yaml", "pyYAML")]
             If modul is not imprtable but an CLI-TOOL, set import_name to ""
    """
    for import_name, pip_name in modules:
        if import_name:
            # if import_name set, try to impoert the module first
            try:
                importlib.import_module(import_name)
                print(f"[installModules] ✔️ Modul '{import_name}' already installed.")
                continue
            except ImportError:
                print(f"[installModules] ⚠️ Modul '{import_name}' not found. Try installation of '{pip_name}'...")
        else:
            print(f"[installModules] ℹ️ CLI-Modul '{pip_name}' – will only be checked by pip...")

        # installation if not already installed, or it is a CLI-TOOL
        try:
            #pip_name is validadet --> safe to call subprozess
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
        except subprocess.CalledProcessError:
            print(f"[installModules] ❌ Error during installation of '{pip_name}'. Install it manually!")
            sys.exit(1)

        # after installation: test import again, if it is not just a cli-tool
        if import_name:
            try:
                importlib.import_module(import_name)
                print(f"[installModules] ✔️ Modul '{import_name}' successfully installed.")
            except ImportError:
                print(f"[installModules] ❌ Modulimport '{import_name}' was not successful after installation.")
                sys.exit(1)
        else:
            print(f"[installModules] ✔️ CLI-Modul '{pip_name}' successfully installed.")