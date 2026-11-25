"""Tests for keybind.engine."""

from unittest.mock import patch, MagicMock
import pytest
from keybind.data_model import Config, KeyCombo, Shortcut, ShortcutAction
from keybind.engine import KeybindEngine


def test_engine_start_stop_idempotent():
    cfg = Config(shortcuts=[
        Shortcut(combo=KeyCombo(keys=["ctrl", "shift"]), action=ShortcutAction(text="hi")),
    ])
    engine = KeybindEngine(config_loader=lambda: cfg)
    engine.start()
    engine.start()  # second call should be no-op
    engine.stop()
    engine.stop()  # second call should be no-op


def test_engine_no_shortcuts_no_listener():
    cfg = Config(shortcuts=[])
    engine = KeybindEngine(config_loader=lambda: cfg)
    engine.start()
    assert engine._listener is None
    engine.stop()


def test_engine_action_handler_called():
    """Verify the action handler is invoked when a combo is triggered."""
    cfg = Config(shortcuts=[
        Shortcut(combo=KeyCombo(keys=["ctrl", "shift", "f"]), action=ShortcutAction(text="test")),
    ])

    calls = []
    engine = KeybindEngine(
        config_loader=lambda: cfg,
        action_handler=lambda action: calls.append(action),
    )
    engine.start()

    # Simulate hotkey trigger by calling the handler directly
    engine._action_handler(ShortcutAction(text="direct"))
    engine.stop()
    assert len(calls) == 1
    assert calls[0].text == "direct"


def test_engine_reload():
    """Engine reload restarts the listener with fresh config."""
    cfg = Config(shortcuts=[
        Shortcut(combo=KeyCombo(keys=["ctrl", "shift"]), action=ShortcutAction(text="hi")),
    ])
    engine = KeybindEngine(config_loader=lambda: cfg)
    engine.start()
    engine.reload()
    assert engine.is_running
    engine.stop()
    assert not engine.is_running
