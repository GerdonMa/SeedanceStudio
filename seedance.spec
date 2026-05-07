# -*- mode: python ; coding: utf-8 -*-
"""
Seedance Studio PyInstaller 打包配置.

使用方法: pyinstaller seedance.spec
输出: dist/SeedanceStudio.exe
"""

import sys
from pathlib import Path

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/templates/prompt_templates.json', 'assets/templates'),
    ],
    hiddenimports=[
        'volcenginesdkarkruntime',
        'PyQt6.QtMultimedia',
        'PyQt6.QtMultimediaWidgets',
        'sqlite3',
        'logging.handlers',
        # Phase 8 主题系统（确保静态 import 的模块被 PyInstaller 收集）
        'themes',
        'themes.theme_loader',
        'themes.builtin',
        'themes.builtin.default_light',
        'themes.builtin.default_dark',
        'themes.builtin.marathon.fx',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SeedanceStudio',
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
    icon=None,  # TODO: 修复 app.ico 后改回 'assets/icons/app.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SeedanceStudio',
)
