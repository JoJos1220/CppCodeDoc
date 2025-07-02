# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\000_ProjectData\\999_Sonstiges\\VSCode\\CppCodeDoc-private\\src\\CppCodeDoc.py'],
    pathex=['./src'],
    binaries=[],
    datas=[('LICENSE.txt', 'assets\\LICENSE'), ('help.md', 'assets'), ('changelog.md', 'assets'), ('.\\src\\lang', 'assets\\lang'), ('.\\src\\fileExamples\\testFile.h', 'assets\\fileExamples'), ('.\\src\\config.yaml', 'assets'), ('.\\src\\generator\\img\\logo.svg', 'assets'), ('.\\src\\generator\\img\\Ko-fi.svg', 'assets'), ('.\\src\\generator\\img\\paypal.svg', 'assets'), ('.\\src\\generator\\img\\github.svg', 'assets'), ('.\\src\\generator\\img\\DarkMode.svg', 'assets'), ('.\\src\\utils\\icon\\icon.ico', 'assets'), ('.\\src\\utils\\icon\\FileExtension.ico', 'assets'), ('.\\src\\generator\\img\\Reference.png', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CppCodeDoc',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='C:\\000_ProjectData\\999_Sonstiges\\VSCode\\CppCodeDoc-private\\scripts\\version_info.txt',
    uac_admin=True,
    icon=['src\\utils\\icon\\icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CppCodeDoc',
)
