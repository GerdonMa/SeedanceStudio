"""
设置用例单元测试。

测试 SettingsUseCase 的配置读写和 API 连通性检测。
"""
from __future__ import annotations

import logging
import unittest
from unittest.mock import MagicMock

from infrastructure.config_store import ConfigStore
from core.event_bus import EventBus
from application.settings_usecase import SettingsUseCase


class TestSettingsUseCase(unittest.TestCase):
    """设置用例测试"""

    def setUp(self):
        self.config = ConfigStore(logging.getLogger("test"))
        self.event_bus = EventBus.instance()
        self.logger = logging.getLogger("test")
        self.logger.setLevel(logging.CRITICAL)

    def test_save_and_load_preference(self):
        usecase = SettingsUseCase(self.config, self.event_bus, self.logger)

        usecase.save_preference("default_model", "doubao-seedance-2-0-fast-260128")
        prefs = usecase.load_preferences()
        self.assertEqual(prefs["default_model"], "doubao-seedance-2-0-fast-260128")

    def test_get_preference_with_default(self):
        usecase = SettingsUseCase(self.config, self.event_bus, self.logger)

        self.assertEqual(usecase.get_preference("nonexistent", 42), 42)
        self.assertEqual(usecase.get_preference("nonexistent", "fallback"), "fallback")

    def test_save_preference_emits_event(self):
        usecase = SettingsUseCase(self.config, self.event_bus, self.logger)

        received = []
        self.event_bus.settings_changed.connect(lambda: received.append(True))

        usecase.save_preference("default_duration", 10)
        self.assertTrue(received)

    def test_multiple_preferences(self):
        usecase = SettingsUseCase(self.config, self.event_bus, self.logger)

        usecase.save_preference("dark_mode", True)
        usecase.save_preference("window_width", 1400)
        usecase.save_preference("default_resolution", "1080p")

        prefs = usecase.load_preferences()
        self.assertTrue(prefs["dark_mode"])
        self.assertEqual(prefs["window_width"], 1400)
        self.assertEqual(prefs["default_resolution"], "1080p")

    def test_test_connection_no_api_client(self):
        usecase = SettingsUseCase(self.config, self.event_bus, self.logger, None)

        ok, msg = usecase.test_connection()
        self.assertFalse(ok)

    def test_test_connection_with_api_client(self):
        mock_api = MagicMock()
        mock_api.test_connection.return_value = (True, "Connected successfully")

        usecase = SettingsUseCase(self.config, self.event_bus, self.logger, mock_api)

        ok, msg = usecase.test_connection()
        self.assertTrue(ok)
        self.assertIn("Connected", msg)

    def test_test_connection_api_error(self):
        mock_api = MagicMock()
        mock_api.test_connection.return_value = (False, "Connection timeout")

        usecase = SettingsUseCase(self.config, self.event_bus, self.logger, mock_api)

        ok, msg = usecase.test_connection()
        self.assertFalse(ok)
        self.assertIn("timeout", msg)


if __name__ == "__main__":
    unittest.main()
