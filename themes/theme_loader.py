"""
主题加载器。

扫描内置、社区、用户目录中的主题包，验证并注册到 ThemeRegistry。
"""
from __future__ import annotations

import importlib.util
import json
import logging
import os
import shutil
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING

from themes import ThemeInfo, ThemeRegistry

if TYPE_CHECKING:
    pass

_BUILTIN_DIR = Path(__file__).parent / "builtin"
_COMMUNITY_DIR = Path(__file__).parent / "community"
_USER_THEMES_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "SeedanceStudio" / "themes"


class ThemeLoader:
    """主题加载器：扫描 → 验证 → 注册"""

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def discover_all(self) -> list[ThemeInfo]:
        """
        扫描所有主题源，返回 ThemeInfo 列表。
        内置主题：静态 import（PyInstaller 兼容）
        社区 / 用户主题：文件系统扫描
        后加载的同名 ID 覆盖先加载的。
        """
        themes: list[ThemeInfo] = []

        # 内置主题：静态 import
        builtin = self._load_builtin_themes()
        for theme in builtin:
            ThemeRegistry.register(theme)
            themes.append(theme)

        # 社区主题：文件系统扫描
        if _COMMUNITY_DIR.exists():
            discovered = self._scan_directory(_COMMUNITY_DIR)
            for theme in discovered:
                ThemeRegistry.register(theme)
                themes.append(theme)
            self._logger.info(f"ThemeLoader: community → {len(discovered)} themes loaded")

        # 用户主题：文件系统扫描
        if _USER_THEMES_DIR.exists():
            discovered = self._scan_directory(_USER_THEMES_DIR)
            for theme in discovered:
                ThemeRegistry.register(theme)
                themes.append(theme)
            self._logger.info(f"ThemeLoader: user → {len(discovered)} themes loaded")

        self._logger.info(
            f"ThemeLoader: total {len(ThemeRegistry.list_all())} themes registered"
        )
        return themes

    def _load_builtin_themes(self) -> list[ThemeInfo]:
        """
        静态 import 加载内置主题（PyInstaller 兼容）。

        PyInstaller 通过静态分析 import 链收集模块。使用 importlib 动态加载
        的模块不会被自动打包。因此内置主题使用显式 import 语句。
        """
        themes: list[ThemeInfo] = []

        try:
            from themes.builtin.graphite import (
                THEME_MANIFEST as m, THEME_QSS as q, SIDEBAR_QSS as s,
            )
            import themes.builtin.graphite as graphite_fx
            themes.append(ThemeInfo(
                id=m["id"], name=m["name"], qss=q, sidebar_qss=s,
                is_dark=m["is_dark"], manifest=m, fx_module=graphite_fx,
            ))
        except Exception as e:
            self._logger.error(f"Failed to load builtin theme graphite: {e}")

        try:
            from themes.builtin.swiss import (
                THEME_MANIFEST as m, THEME_QSS as q, SIDEBAR_QSS as s,
            )
            import themes.builtin.swiss as swiss_fx
            themes.append(ThemeInfo(
                id=m["id"], name=m["name"], qss=q, sidebar_qss=s,
                is_dark=m["is_dark"], manifest=m, fx_module=swiss_fx,
            ))
        except Exception as e:
            self._logger.error(f"Failed to load builtin theme swiss: {e}")

        self._logger.info(f"ThemeLoader: builtin → {len(themes)} themes loaded (static import)")
        return themes

    def _scan_directory(self, directory: Path) -> list[ThemeInfo]:
        """扫描目录，发现所有主题"""
        themes: list[ThemeInfo] = []

        if not directory.exists():
            return themes

        for entry in sorted(directory.iterdir()):
            # 跳过隐藏文件和 readme
            if entry.name.startswith(".") or entry.suffix.lower() == ".txt":
                continue

            theme = None

            if entry.is_dir():
                theme = self._scan_manifest_dir(entry)
            elif entry.suffix == ".py":
                theme = self._scan_py_file(entry)

            if theme is not None:
                themes.append(theme)

        return themes

    def _scan_manifest_dir(self, directory: Path) -> ThemeInfo | None:
        """从包含 manifest.json 的目录加载主题（目录型）"""
        manifest_path = directory / "manifest.json"
        if not manifest_path.exists():
            self._logger.warning(f"ThemeLoader: {directory.name} missing manifest.json, skipped")
            return None

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except json.JSONDecodeError as e:
            self._logger.warning(f"ThemeLoader: {directory.name} invalid manifest.json: {e}")
            return None

        errors = self._validate_manifest(manifest)
        if errors:
            self._logger.warning(
                f"ThemeLoader: {directory.name} manifest validation failed: {errors}"
            )
            return None

        # 读取 QSS 文件
        qss = self._read_qss_file(directory, manifest)
        sidebar_qss = self._read_sidebar_qss_file(directory, manifest)
        fx_module = self._load_fx_module(directory)

        theme_id = manifest["id"]
        self._logger.info(f"ThemeLoader: loaded directory theme '{theme_id}' from {directory.name}")
        return ThemeInfo(
            id=theme_id,
            name=manifest.get("name", theme_id),
            qss=qss,
            sidebar_qss=sidebar_qss,
            is_dark=manifest.get("is_dark", False),
            manifest=manifest,
            fx_module=fx_module,
        )

    def _scan_py_file(self, filepath: Path) -> ThemeInfo | None:
        """从单个 .py 文件加载主题（单文件型）"""
        module_name = filepath.stem

        try:
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if spec is None or spec.loader is None:
                self._logger.warning(f"ThemeLoader: cannot load {filepath.name}")
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            self._logger.warning(f"ThemeLoader: failed to import {filepath.name}: {e}")
            return None

        manifest = getattr(module, "THEME_MANIFEST", None)
        if not isinstance(manifest, dict):
            self._logger.warning(f"ThemeLoader: {filepath.name} missing THEME_MANIFEST dict, skipped")
            return None

        errors = self._validate_manifest(manifest)
        if errors:
            self._logger.warning(
                f"ThemeLoader: {filepath.name} manifest validation failed: {errors}"
            )
            return None

        qss = getattr(module, "THEME_QSS", "")
        sidebar_qss = getattr(module, "SIDEBAR_QSS", "")
        fx_module = module if any(
            hasattr(module, attr) for attr in ["fade_in", "fade_out", "on_theme_activated"]
        ) else None

        theme_id = manifest["id"]
        self._logger.info(f"ThemeLoader: loaded .py theme '{theme_id}' from {filepath.name}")
        return ThemeInfo(
            id=theme_id,
            name=manifest.get("name", theme_id),
            qss=qss,
            sidebar_qss=sidebar_qss,
            is_dark=manifest.get("is_dark", False),
            manifest=manifest,
            fx_module=fx_module,
        )

    def import_zip(self, zip_path: str) -> ThemeInfo | None:
        """
        导入 .zip 主题包，解压到用户 APPDATA 目录。

        Args:
            zip_path: .zip 文件路径

        Returns:
            导入成功返回 ThemeInfo，失败返回 None
        """
        zip_file = Path(zip_path)
        if not zip_file.exists() or zip_file.suffix.lower() != ".zip":
            self._logger.warning(f"ThemeLoader: invalid zip path: {zip_path}")
            return None

        try:
            _USER_THEMES_DIR.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_file, "r") as zf:
                # 安全检查：防止 zip slip 攻击
                for member in zf.namelist():
                    member_path = _USER_THEMES_DIR / member
                    if not str(member_path.resolve()).startswith(str(_USER_THEMES_DIR.resolve())):
                        self._logger.error(f"ThemeLoader: zip slip attack detected: {member}")
                        return None

                zf.extractall(_USER_THEMES_DIR)

            self._logger.info(f"ThemeLoader: imported theme from {zip_file.name}")
            # 重新扫描用户目录
            themes = self._scan_directory(_USER_THEMES_DIR)
            for theme in themes:
                ThemeRegistry.register(theme)
            return themes[-1] if themes else None

        except zipfile.BadZipFile as e:
            self._logger.error(f"ThemeLoader: bad zip file: {e}")
            return None
        except Exception as e:
            self._logger.error(f"ThemeLoader: import failed: {e}")
            return None

    def install_py(self, py_path: str) -> ThemeInfo | None:
        """
        安装单个 .py 主题文件到用户 APPDATA 目录。

        Args:
            py_path: .py 文件路径

        Returns:
            安装成功返回 ThemeInfo，失败返回 None
        """
        source = Path(py_path)
        if not source.exists() or source.suffix != ".py":
            self._logger.warning(f"ThemeLoader: invalid .py path: {py_path}")
            return None

        try:
            _USER_THEMES_DIR.mkdir(parents=True, exist_ok=True)
            dest = _USER_THEMES_DIR / source.name
            shutil.copy2(source, dest)
            self._logger.info(f"ThemeLoader: installed .py theme: {source.name}")
            return self._scan_py_file(dest)
        except Exception as e:
            self._logger.error(f"ThemeLoader: install_py failed: {e}")
            return None

    def _validate_manifest(self, manifest: dict) -> list[str]:
        """验证 manifest 合法性，返回错误列表"""
        errors: list[str] = []

        required_fields = [
            ("id", str),
            ("name", str),
            ("version", str),
            ("author", str),
            ("is_dark", bool),
        ]

        for field, expected_type in required_fields:
            if field not in manifest:
                errors.append(f"缺少必选字段: {field}")
            elif not isinstance(manifest[field], expected_type):
                errors.append(f"字段类型错误: {field} 应为 {expected_type.__name__}")

        if "manifest_version" not in manifest:
            errors.append("缺少必选字段: manifest_version")
        elif manifest["manifest_version"] != 1:
            errors.append(f"不支持的 manifest_version: {manifest['manifest_version']}")

        return errors

    @staticmethod
    def _read_qss_file(directory: Path, manifest: dict) -> str:
        """读取 theme.qss 文件"""
        qss_path = directory / "theme.qss"
        if qss_path.exists():
            return qss_path.read_text(encoding="utf-8")
        # 回退：尝试从 manifest 指定的文件
        return ""

    @staticmethod
    def _read_sidebar_qss_file(directory: Path, manifest: dict) -> str:
        """读取 sidebar.qss 文件"""
        sidebar_path = directory / "sidebar.qss"
        if sidebar_path.exists():
            return sidebar_path.read_text(encoding="utf-8")
        return ""

    @staticmethod
    def _load_fx_module(directory: Path) -> object | None:
        """加载可选的 fx.py 动效模块"""
        fx_path = directory / "fx.py"
        if not fx_path.exists():
            return None
        try:
            spec = importlib.util.spec_from_file_location(
                f"{directory.name}_fx", fx_path
            )
            if spec is None or spec.loader is None:
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception:
            return None
