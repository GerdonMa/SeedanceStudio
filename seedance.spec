# -*- mode: python ; coding: utf-8 -*-
"""
Seedance Studio PyInstaller 打包配置.

使用方法: pyinstaller seedance.spec
输出: dist/SeedanceStudio-v1.3.0.exe
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
        # 主题系统（静态 import，显式列出确保被收集）
        'themes',
        'themes.theme_loader',
        'themes.builtin.graphite',
        'themes.builtin.swiss',
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
    name='SeedanceStudio-v1.3.0',
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
    icon=None,  # app.ico 格式不被 PIL 识别，需修复图标文件
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SeedanceStudio-v1.3.0',
)
