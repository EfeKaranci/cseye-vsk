# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['_a_main.py'],
    pathex=[],
    binaries=[],
    datas=[('qtDesigner', 'qtDesigner'), ('images', 'images'), ('Planes', 'Planes'), ('Hooks', 'Hooks'), ('PlottingFunctions', 'PlottingFunctions'), ('GetSelectedObjects', 'GetSelectedObjects'), ('SpreadsheetFunctions', 'SpreadsheetFunctions'), ('database', 'database'), ('states', 'states')],
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
    name='ETABSToolbox',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ETABSToolbox',
)
