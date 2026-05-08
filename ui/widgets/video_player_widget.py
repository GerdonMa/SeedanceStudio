"""
视频播放器组件。

使用 QtMultimedia 内嵌播放视频，显示任务详情和下载按钮。
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QMessageBox,
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

from core.di_container import Container


class VideoPlayerWidget(QWidget):
    """视频播放器组件"""

    def __init__(self, container: Container, task_id: str, video_url: str):
        super().__init__()
        self._container = container
        self._task_id = task_id
        self._video_url = video_url
        self._init_ui()
        self._load_video()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 视频播放区
        self._video_widget = QVideoWidget()
        self._video_widget.setMinimumSize(480, 270)

        self._media_player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self._media_player.setAudioOutput(self._audio_output)
        self._media_player.setVideoOutput(self._video_widget)
        layout.addWidget(self._video_widget)

        # 信息栏
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.StyledPanel)
        info_layout = QVBoxLayout()

        self._url_label = QLabel("URL 加载中...")
        self._url_label.setWordWrap(True)
        self._url_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        info_layout.addWidget(self._url_label)

        self._expiry_label = QLabel("视频 URL 有效期为 24 小时，请及时下载")
        self._expiry_label.setObjectName("expiryLabel")
        info_layout.addWidget(self._expiry_label)

        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)

        # 按钮栏
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        copy_btn = QPushButton("复制 URL")
        copy_btn.clicked.connect(self._on_copy_url)
        btn_layout.addWidget(copy_btn)

        download_btn = QPushButton("下载视频")
        download_btn.clicked.connect(self._on_download)
        download_btn.setObjectName("downloadButton")
        download_btn.setProperty("role", "primary")
        btn_layout.addWidget(download_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _load_video(self):
        self._media_player.setSource(QUrl(self._video_url))
        self._url_label.setText(self._video_url)

    def _on_copy_url(self):
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(self._video_url)

    def _on_download(self):
        try:
            from PyQt6.QtWidgets import QFileDialog
            from pathlib import Path
            
            default_dir = self._container.settings_usecase.get_preference("download_path", str(Path.home() / "Desktop"))
            default_path = str(Path(default_dir) / "seedance_video.mp4")
            
            save_path, _ = QFileDialog.getSaveFileName(
                self, "保存视频", default_path, "Video Files (*.mp4)"
            )
            if save_path:
                actual_path = self._container.download_usecase.download_video(self._video_url, save_path)
                QMessageBox.information(self, "下载完成", f"视频已保存到:\n{actual_path}")
        except Exception as e:
            QMessageBox.critical(self, "下载失败", f"下载视频失败：{e}\n\n请确认视频 URL 仍然有效（24小时内）以及网络连接正常。")

    def closeEvent(self, event):
        self._media_player.stop()
        super().closeEvent(event)
