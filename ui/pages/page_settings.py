"""
设置页面。

提供 API Key 配置、偏好设置等功能。
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QFormLayout, QFileDialog,
    QCheckBox, QComboBox
)
from PyQt6.QtCore import Qt

from core.di_container import Container
from themes import ThemeRegistry


class SettingsPage(QWidget):
    """设置页面"""
    
    def __init__(self, container: Container):
        super().__init__()
        self._container = container
        self._init_ui()
        self._load_settings()
    
    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("设置")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        
        # 表单
        form = QFormLayout()
        form.setSpacing(15)
        
        # API Key
        self._api_key_input = QLineEdit()
        self._api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._api_key_input.setPlaceholderText("请输入火山引擎 API Key")
        form.addRow("API Key:", self._api_key_input)
        
        # Base URL
        self._base_url_input = QLineEdit()
        self._base_url_input.setPlaceholderText("https://ark.cn-beijing.volces.com/api/v3")
        form.addRow("Base URL:", self._base_url_input)
        
        # Download Path
        download_row = QHBoxLayout()
        self._download_path_input = QLineEdit()
        self._download_path_input.setPlaceholderText("默认下载路径（桌面）")
        download_row.addWidget(self._download_path_input)
        
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self._on_browse_download_path)
        download_row.addWidget(browse_btn)
        form.addRow("下载路径:", download_row)
        
        layout.addLayout(form)

        # 外观设置 — 下拉菜单选择 UI 风格
        appearance_layout = QHBoxLayout()
        appearance_layout.addWidget(QLabel("UI 风格:"))
        self._theme_combo = QComboBox()
        for theme in ThemeRegistry.list_all():
            self._theme_combo.addItem(theme.name, theme.id)
        appearance_layout.addWidget(self._theme_combo)
        appearance_layout.addStretch()
        layout.addLayout(appearance_layout)
        
        layout.addSpacing(10)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self._save_btn = QPushButton("保存")
        self._save_btn.setProperty("role", "primary")
        self._save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(self._save_btn)
        
        self._test_btn = QPushButton("测试连接")
        self._test_btn.setProperty("role", "ghost")
        self._test_btn.clicked.connect(self._on_test)
        btn_layout.addWidget(self._test_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        self.setLayout(layout)

        self._theme_combo.currentIndexChanged.connect(self._on_theme_changed)

    def _on_theme_changed(self, index: int):
        """UI 风格切换"""
        if index < 0:
            return
        theme_id = self._theme_combo.currentData()
        if not theme_id:
            return
        self._container.settings_usecase.save_preference("ui_theme", theme_id)
        self._container.event_bus.theme_changed.emit(theme_id)
    
    def _load_settings(self):
        """加载设置"""
        if self._container is None:
            return
        prefs = self._container.settings_usecase.load_preferences()
        self._api_key_input.setText(prefs.get("api_key", ""))
        self._base_url_input.setText(prefs.get("base_url", ""))
        self._download_path_input.setText(prefs.get("download_path", ""))
        theme_id = prefs.get("ui_theme", ThemeRegistry.default_id())
        idx = self._theme_combo.findData(theme_id)
        if idx >= 0:
            self._theme_combo.setCurrentIndex(idx)
    
    def _on_save(self):
        """保存设置"""
        try:
            api_key = self._api_key_input.text().strip()
            base_url = self._base_url_input.text().strip()
            
            if not api_key:
                QMessageBox.warning(self, "警告", "API Key 不能为空")
                return
            
            self._container.settings_usecase.save_preference("api_key", api_key)
            self._container.settings_usecase.save_preference("base_url", base_url)
            
            download_path = self._download_path_input.text().strip()
            if download_path:
                self._container.settings_usecase.save_preference("download_path", download_path)
            
            QMessageBox.information(self, "成功", "设置已保存")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
    
    def _on_test(self):
        """测试连接"""
        try:
            api_key = self._api_key_input.text().strip()
            base_url = self._base_url_input.text().strip()
            self._container.settings_usecase.save_preference("api_key", api_key)
            self._container.settings_usecase.save_preference("base_url", base_url)
            
            download_path = self._download_path_input.text().strip()
            if download_path:
                self._container.settings_usecase.save_preference("download_path", download_path)
            
            success, message = self._container.settings_usecase.test_connection()
            if success:
                QMessageBox.information(self, "成功", message)
            else:
                QMessageBox.warning(self, "失败", message)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"测试失败: {str(e)}")
    
    def _on_browse_download_path(self):
        """选择下载路径"""
        path = QFileDialog.getExistingDirectory(self, "选择默认下载目录", self._download_path_input.text())
        if path:
            self._download_path_input.setText(path)
            if self._container is not None:
                self._container.settings_usecase.save_preference("download_path", path)
