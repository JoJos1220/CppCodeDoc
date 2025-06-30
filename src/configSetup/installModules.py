# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys, importlib, subprocess

def ensure_modules(modules):
    """
    modules: list of datatype tuple (import_name, pip_name)
             e.g. [("yaml", "pyYAML")]
    """
    for import_name, pip_name in modules:
        try:
            importlib.import_module(import_name)
            print(f"[installModules] ✔️ Modul '{import_name}' already installed.")
        except ImportError:
            print(f"[installModules] ⚠️ Modul '{import_name}' not found. Try installation of '{pip_name}'...")

            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
                importlib.import_module(import_name)
                print(f"[installModules] ✔️ Modul '{import_name}' successfully installed.")
            except subprocess.CalledProcessError:
                print(f"[installModules] ❌ Error during installation of '{pip_name}'. Install it manually!")
                sys.exit(1)
            except ImportError:
                print(f"[installModules] ❌ Modulimport '{import_name}' was not successfull after installation.")
                sys.exit(1)