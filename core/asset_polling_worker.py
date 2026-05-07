"""
资产审核轮询 Worker。

使用 QThread 每 10 秒轮询待审核资产的审核状态，通过 EventBus 广播审核结果。
"""
from __future__ import annotations

import logging
import threading

from PyQt6.QtCore import QThread

from core.event_bus import EventBus


_ASSET_POLL_INTERVAL = 10


class AssetPollingWorker(QThread):
    """资产审核状态轮询工作线程"""

    def __init__(
        self,
        asset_usecase,
        event_bus: EventBus,
        logger: logging.Logger,
    ):
        super().__init__()
        self._asset_usecase = asset_usecase
        self._event_bus = event_bus
        self._logger = logger
        self._pending_assets: list[str] = []
        self._lock = threading.Lock()
        self._running = True

    def run(self):
        """轮询线程主循环，内部全覆盖 try/except"""
        self._logger.info("AssetPollingWorker started")
        while self._running:
            try:
                self._poll_all()
            except Exception as e:
                self._logger.error(f"Asset polling error: {e}", exc_info=True)
                self._event_bus.error_occurred.emit("ASSET_POLL_ERROR", str(e))

            QThread.sleep(_ASSET_POLL_INTERVAL)

    def _poll_all(self):
        """轮询所有待审核资产"""
        with self._lock:
            assets = list(self._pending_assets)

        for asset_id in assets:
            try:
                status = self._asset_usecase.get_asset_status(asset_id)

                if status == "approved":
                    self._event_bus.asset_approved.emit(asset_id)
                    with self._lock:
                        if asset_id in self._pending_assets:
                            self._pending_assets.remove(asset_id)
                    self._logger.info(f"Asset approved: {asset_id}")
                elif status == "rejected":
                    reason = self._get_reject_reason(asset_id)
                    self._event_bus.asset_rejected.emit(asset_id, reason)
                    with self._lock:
                        if asset_id in self._pending_assets:
                            self._pending_assets.remove(asset_id)
                    self._logger.warning(f"Asset rejected: {asset_id}, reason={reason}")

            except Exception as e:
                self._logger.error(f"Failed to poll asset {asset_id}: {e}")

    def _get_reject_reason(self, asset_id: str) -> str:
        """获取资产被拒原因"""
        try:
            return self._asset_usecase.get_reject_reason(asset_id)
        except Exception:
            return "未知原因"

    def add_asset(self, asset_id: str):
        """添加待审核资产到轮询队列（线程安全，可由任意线程调用）"""
        with self._lock:
            if asset_id not in self._pending_assets:
                self._pending_assets.append(asset_id)
                self._logger.info(f"Asset added to polling queue: {asset_id}")

    def stop(self):
        """停止轮询线程"""
        self._running = False
        self.wait()
        self._logger.info("AssetPollingWorker stopped")
