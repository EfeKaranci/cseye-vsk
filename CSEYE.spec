# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['_a_main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('images', 'images'),
        ('qtDesigner', 'qtDesigner'),
        ('database', 'database'),
        ('states', 'states'),
        ('Hooks', 'Hooks'),
        ('Planes', 'Planes'),
        ('PlottingFunctions', 'PlottingFunctions'),
        ('GetSelectedObjects', 'GetSelectedObjects'),
        ('SpreadsheetFunctions', 'SpreadsheetFunctions'),
    ],
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'pandas',
        'numpy',
        'matplotlib',
        'openpyxl',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CSEYE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='images/icon.png',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CSEYE',
)
