"""
任务缩略图服务。

用 QMediaPlayer + QVideoSink 从已生成视频抓取一帧作为预览图，
缓存到 %APPDATA%/SeedanceStudio/thumbs/{task_id}.png。
单实例串行处理请求队列；失败任务记入内存集合避免重复请求。
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from PyQt6.QtCore import QObject, QUrl, Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QImage
from PyQt6.QtMultimedia import QMediaPlayer, QVideoSink

_THUMB_WIDTH = 192  # 缓存帧宽（16:9 → 192×108），兼顾清晰与体积


class ThumbnailService(QObject):
    """视频首帧缩略图抓取服务（单例）"""

    thumbnail_ready = pyqtSignal(str)  # task_id（缓存文件就绪）

    _instance: "ThumbnailService | None" = None

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._logger = logging.getLogger("SeedanceStudio")
        self._queue: list[tuple[str, str]] = []   # (task_id, video_url)
        self._failed: set[str] = set()
        self._busy = False
        self._current: tuple[str, str] | None = None
        self._got_frame = False

        self._cache_dir = Path(
            os.getenv("APPDATA", str(Path.home()))
        ) / "SeedanceStudio" / "thumbs"
        try:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self._logger.warning(f"Thumbnail cache dir unavailable: {e}")

        self._player = QMediaPlayer(self)
        self._player.errorOccurred.connect(self._on_error)
        self._player.mediaStatusChanged.connect(self._on_status)
        self._sink = QVideoSink(self)
        self._player.setVideoSink(self._sink)
        self._sink.videoFrameChanged.connect(
            lambda frame: self._on_frame(frame.toImage())
        )

        # 抓帧后 8 秒仍未完成 → 视为失败，防止队列卡死
        self._timeout = QTimer(self)
        self._timeout.setSingleShot(True)
        self._timeout.timeout.connect(self._on_timeout)

    @classmethod
    def instance(cls) -> "ThumbnailService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ---- 对外接口 ----

    def thumbnail_path(self, task_id: str) -> Path | None:
        """返回缓存缩略图路径（不存在则 None）"""
        path = self._cache_dir / f"{task_id}.png"
        return path if path.exists() else None

    def request(self, task_id: str, video_url: str) -> None:
        """请求生成缩略图（缓存命中或已在队列则忽略）"""
        if not video_url:
            return
        if task_id in self._failed:
            return
        if self.thumbnail_path(task_id) is not None:
            self.thumbnail_ready.emit(task_id)
            return
        if any(tid == task_id for tid, _ in self._queue):
            return
        if self._current and self._current[0] == task_id:
            return
        self._queue.append((task_id, video_url))
        self._pump()

    # ---- 内部处理 ----

    def _pump(self) -> None:
        if self._busy or not self._queue:
            return
        self._busy = True
        self._got_frame = False
        self._current = self._queue.pop(0)
        task_id, url = self._current
        self._player.setSource(QUrl(url))
        self._player.pause()  # 加载元数据以便 seek
        self._timeout.start(8000)

    def _on_status(self, status) -> None:
        if self._current is None or not self._busy:
            return
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            duration = self._player.duration()
            # 取 1 秒处；短视频取 1/4 处，保证画面已进入正片
            pos = 1000 if duration > 4000 else max(1, duration // 4)
            self._player.setPosition(pos)

    def _on_frame(self, frame_image: QImage) -> None:
        """由 videoSink 回调传入一帧（见 _install_sink 中的连接）"""
        if self._got_frame or self._current is None:
            return
        self._got_frame = True
        task_id, _ = self._current
        try:
            scaled = frame_image.scaledToWidth(
                _THUMB_WIDTH, Qt.TransformationMode.SmoothTransformation
            )
            path = self._cache_dir / f"{task_id}.png"
            scaled.save(str(path), "PNG")
            self.thumbnail_ready.emit(task_id)
        except Exception as e:
            self._logger.warning(f"Failed to save thumbnail for {task_id}: {e}")
        finally:
            self._finish()

    def _on_error(self, _error, msg: str) -> None:
        if self._current is None:
            return
        task_id, _ = self._current
        self._logger.info(f"Thumbnail fetch failed for {task_id}: {msg}")
        self._failed.add(task_id)
        self._finish()

    def _on_timeout(self) -> None:
        if self._current is None:
            return
        task_id, _ = self._current
        self._logger.info(f"Thumbnail fetch timeout for {task_id}")
        self._failed.add(task_id)
        self._finish()

    def _finish(self) -> None:
        self._timeout.stop()
        self._player.setSource(QUrl())
        self._current = None
        self._busy = False
        self._pump()
