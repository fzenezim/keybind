"""Hotkey engine: monitors global key combos and fires actions."""

import threading
import webbrowser
from typing import Callable, Optional

from .data_model import Shortcut, ShortcutAction

# Keys that pynput treats as modifiers (must be wrapped in <> in hotkey strings)
_MODIFIER_KEYS = {
    "ctrl", "control", "shift", "alt", "win", "windows", "super",
    "cmd", "meta", "altgr", "menu", "fn", "caps",
}


def combo_to_hotkey_str(combo) -> str:
    """Convert a KeyCombo to pynput's GlobalHotKeys string format.

    Modifiers like ctrl/shift/alt are wrapped in angle brackets:
    ["ctrl", "shift", "f"] -> "<ctrl>+<shift>+f"
    """
    parts = []
    for k in combo.keys:
        kl = k.lower()
        if kl in _MODIFIER_KEYS:
            parts.append(f"<{kl}>")
        else:
            parts.append(k)
    return "+".join(parts)


class KeybindEngine:
    """Monitors global keyboard for configured combos and fires actions.

    The engine starts a background thread that uses pynput.GlobalHotKeys
    to listen for all enabled shortcuts. When a combo is pressed, the
    associated action is fired (type text or open URL).
    """

    def __init__(self, config_loader=None, action_handler: Optional[Callable] = None):
        self._config_loader = config_loader or _default_config_loader
        self._action_handler = action_handler or _default_action_handler
        self._listener = None
        self._lock = threading.Lock()
        self._running = False

    def start(self) -> None:
        """Start the hotkey listener. Idempotent."""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._start_listener()

    def stop(self) -> None:
        """Stop the hotkey listener. Idempotent."""
        with self._lock:
            if not self._running:
                return
            self._running = False
            if self._listener is not None:
                try:
                    self._listener.stop()
                except Exception:
                    pass
                self._listener = None

    def reload(self) -> None:
        """Reload configuration and restart the listener with new shortcuts."""
        with self._lock:
            self._stop_listener_unlocked()
            self._running = True
            self._start_listener()

    def _stop_listener_unlocked(self):
        if self._listener is not None:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None

    def _start_listener(self):
        from pynput import keyboard

        config = self._config_loader()
        shortcuts = config.get_enabled_shortcuts()
        if not shortcuts:
            self._listener = None
            return

        combo_map = {}
        for sc in shortcuts:
            combo_str = combo_to_hotkey_str(sc.combo)
            combo_map[combo_str] = sc

        def on_hotkey(combo_str):
            sc = combo_map.get(combo_str)
            if sc:
                self._action_handler(sc.action)

        handlers = {
            cs: (lambda s, cs=cs: on_hotkey(cs)) for cs in combo_map
        }

        self._listener = keyboard.GlobalHotKeys(handlers)
        self._listener.daemon = True
        self._listener.start()

    @property
    def is_running(self) -> bool:
        return self._running


def _default_config_loader():
    from .data_model import Config
    return Config.load()


def _default_action_handler(action: ShortcutAction) -> None:
    """Built-in handler: type text with pyautogui or open URL in browser."""
    if action.is_link:
        url = action.url.strip()
        if url:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            webbrowser.open(url)
    else:
        text = action.text
        if text:
            import pyautogui
            pyautogui.write(text)
