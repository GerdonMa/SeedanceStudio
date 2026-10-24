"""
视频预览播放器窗口。

自动播放 + 播放/暂停、进度拖动、音量控制、过期/网络错误提示。
主题样式跟随全局 QSS（卡片信息区 + 标准控件）。
"""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QSlider, QSizePolicy,
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

from core.di_container import Container
from ui.widgets.pro_icons import play_icon, pause_icon


def _fmt_ms(ms: int) -> str:
    """毫秒 → mm:ss"""
    s = max(0, ms // 1000)
    return f"{s // 60:02d}:{s % 60:02d}"


class VideoPlayerWidget(QWidget):
    """视频预览播放器窗口"""

    def __init__(self, container: Container, task_id: str, video_url: str):
        super().__init__()
        self._container = container
        self._task_id = task_id
        self._video_url = video_url
        self._seeking = False
        self._init_ui()
        self._connect_player()
        self._load_video()

    # ---- UI ----

    def _init_ui(self):
        self.setWindowTitle(f"视频预览 — {self._task_id[:16]}")
        self.resize(720, 560)
        self.setMinimumSize(520, 420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 视频播放区（含覆盖提示）
        self._video_widget = QVideoWidget()
        self._video_widget.setMinimumSize(480, 270)
        self._video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self._video_widget, 1)

        self._overlay_label = QLabel("")
        self._overlay_label.setObjectName("pageSub")
        self._overlay_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._overlay_label.setWordWrap(True)
        self._overlay_label.hide()
        layout.addWidget(self._overlay_label)

        # 播放控制条
        controls = QHBoxLayout()
        controls.setSpacing(10)

        self._play_btn = QPushButton()
        self._play_btn.setIcon(play_icon())
        self._play_btn.setFixedSize(34, 30)
        self._play_btn.setToolTip("播放 / 暂停")
        self._play_btn.clicked.connect(self._toggle_play)
        controls.addWidget(self._play_btn)

        self._position_label = QLabel("00:00")
        self._position_label.setObjectName("pageSub")
        controls.addWidget(self._position_label)

        self._seek_slider = QSlider(Qt.Orientation.Horizontal)
        self._seek_slider.setRange(0, 0)
        self._seek_slider.sliderPressed.connect(lambda: setattr(self, "_seeking", True))
        self._seek_slider.sliderReleased.connect(self._on_seek_released)
        self._seek_slider.sliderMoved.connect(
            lambda v: self._position_label.setText(_fmt_ms(v))
        )
        controls.addWidget(self._seek_slider, 1)

        self._duration_label = QLabel("00:00")
        self._duration_label.setObjectName("pageSub")
        controls.addWidget(self._duration_label)

        volume_label = QLabel("音量")
        volume_label.setObjectName("pageSub")
        controls.addWidget(volume_label)
        self._volume_slider = QSlider(Qt.Orientation.Horizontal)
        self._volume_slider.setRange(0, 100)
        self._volume_slider.setValue(80)
        self._volume_slider.setFixedWidth(90)
        self._volume_slider.valueChanged.connect(
            lambda v: self._audio_output.setVolume(v / 100.0)
        )
        controls.addWidget(self._volume_slider)

        layout.addLayout(controls)

        # 信息卡片
        info = QWidget()
        info.setObjectName("statCard")
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(14, 10, 14, 10)
        info_layout.setSpacing(4)

        self._meta_label = QLabel("")
        self._meta_label.setObjectName("pageSub")
        info_layout.addWidget(self._meta_label)

        self._url_label = QLabel(self._video_url)
        self._url_label.setObjectName("pageSub")
        self._url_label.setWordWrap(False)
        self._url_label.setToolTip(self._video_url)
        # 截断显示长 URL，完整内容见 tooltip / 复制按钮
        shown = self._video_url if len(self._video_url) <= 88 else self._video_url[:85] + "..."
        self._url_label.setText(shown)
        info_layout.addWidget(self._url_label)

        expiry = QLabel("视频 URL 有效期 24 小时，过期后请重新生成")
        expiry.setObjectName("pageSub")
        info_layout.addWidget(expiry)

        layout.addWidget(info)

        # 动作条
        actions = QHBoxLayout()
        actions.addStretch()

        copy_btn = QPushButton("复制 URL")
        copy_btn.clicked.connect(self._on_copy_url)
        actions.addWidget(copy_btn)

        download_btn = QPushButton("下载视频")
        download_btn.setProperty("role", "primary")
        download_btn.clicked.connect(self._on_download)
        actions.addWidget(download_btn)

        layout.addLayout(actions)

        # 播放器
        self._media_player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._audio_output.setVolume(0.8)
        self._media_player.setAudioOutput(self._audio_output)
        self._media_player.setVideoOutput(self._video_widget)

    # ---- 播放逻辑 ----

    def _connect_player(self):
        self._media_player.durationChanged.connect(self._on_duration)
        self._media_player.positionChanged.connect(self._on_position)
        self._media_player.playbackStateChanged.connect(self._on_state_changed)
        self._media_player.errorOccurred.connect(self._on_error)

    def _load_video(self):
        self._overlay_label.setText("正在加载视频…")
        self._overlay_label.show()
        self._media_player.setSource(QUrl(self._video_url))
        self._media_player.play()
        self._load_meta()

    def _load_meta(self):
        """从本地任务记录补充模型 / Token 信息（不打 API）"""
        try:
            tasks = self._container.task_usecase.find_all_tasks()
            task = next((t for t in tasks if t.task_id == self._task_id), None)
            if task is not None:
                parts = []
                if task.model:
                    parts.append(f"模型 {task.model}")
                if task.token_usage:
                    parts.append(f"Token {task.token_usage}")
                if task.created_at:
                    parts.append(task.created_at.strftime("生成于 %Y-%m-%d %H:%M"))
                if parts:
                    self._meta_label.setText("  ·  ".join(parts))
        except Exception:
            pass  # 元信息仅为补充展示，失败静默

    def _toggle_play(self):
        state = self._media_player.playbackState()
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self._media_player.pause()
        else:
            self._media_player.play()

    def _on_state_changed(self, state):
        playing = state == QMediaPlayer.PlaybackState.PlayingState
        self._play_btn.setIcon(pause_icon() if playing else play_icon())
        if playing:
            self._overlay_label.hide()

    def _on_duration(self, duration: int):
        self._seek_slider.setRange(0, duration)
        self._duration_label.setText(_fmt_ms(duration))

    def _on_position(self, position: int):
        if not self._seeking:
            self._seek_slider.setValue(position)
        self._position_label.setText(_fmt_ms(position))

    def _on_seek_released(self):
        self._media_player.setPosition(self._seek_slider.value())
        self._seeking = False

    def _on_error(self, _error, msg: str):
        self._overlay_label.setText(
            f"无法播放视频：{msg}\n\n视频 URL 有效期仅 24 小时，过期后请重新生成任务。"
        )
        self._overlay_label.show()

    # ---- 动作 ----

    def _on_copy_url(self):
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(self._video_url)

    def _on_download(self):
        try:
            from PyQt6.QtWidgets import QFileDialog

            default_dir = self._container.settings_usecase.get_preference(
                "download_path", str(Path.home() / "Desktop")
            )
            default_path = str(Path(default_dir) / f"seedance_{self._task_id[:16]}.mp4")

            save_path, _ = QFileDialog.getSaveFileName(
                self, "保存视频", default_path, "Video Files (*.mp4 *.mov)"
            )
            if save_path:
                actual = self._container.download_usecase.download_video(
                    self._video_url, save_path
                )
                QMessageBox.information(self, "下载完成", f"视频已保存到:\n{actual}")
        except Exception as e:
            QMessageBox.critical(
                self, "下载失败",
                f"下载视频失败：{e}\n\n请确认视频 URL 仍然有效（24 小时内）以及网络连接正常。",
            )

    def closeEvent(self, event):
        self._media_player.stop()
        self._media_player.setSource(QUrl())
        super().closeEvent(event)
