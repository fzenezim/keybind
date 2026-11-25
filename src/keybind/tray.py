"""System tray icon for keybind (pystray)."""

import os
import threading

from PIL import Image, ImageDraw, ImageFont
import pystray

from .data_model import Config, KeyCombo, Shortcut, ShortcutAction
from .engine import KeybindEngine


def _make_icon() -> Image.Image:
    """Create a simple 64x64 icon: green circle with 'K'."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Green circle
    draw.ellipse([4, 4, 60, 60], fill=(76, 175, 80, 255))
    # White 'K'
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), "K", font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((64 - tw) / 2 - bbox[0], (64 - th) / 2 - bbox[1]), "K", fill="white", font=font)
    return img


class TrayManager:
    """Manages the system tray icon and engine lifecycle."""

    def __init__(self):
        self._engine: KeybindEngine | None = None
        self._icon: pystray.Icon | None = None
        self._running = False

    def start(self):
        """Start engine + tray icon. Blocks until the icon is closed."""
        self._engine = KeybindEngine()
        self._engine.start()

        icon = pystray.Icon(
            "keybind",
            _make_icon(),
            "keybind - Global Hotkeys",
            pystray.Menu(
                pystray.MenuItem("Open Config", self._open_gui, default=True),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Reload", self._reload),
                pystray.MenuItem("Exit", self._quit),
            ),
        )
        self._icon = icon
        self._running = True
        icon.run()

    def stop(self):
        """Stop engine and tray icon."""
        self._running = False
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None
        if self._engine:
            self._engine.stop()
            self._engine = None

    def _open_gui(self, icon, item):
        """Open the tkinter GUI in a new thread."""
        import tkinter as tk
        from .gui import KeybindApp

        def _run():
            root = tk.Tk()
            app = KeybindApp(root)
            root.mainloop()

        t = threading.Thread(target=_run, daemon=True)
        t.start()

    def _reload(self, icon, item):
        """Reload config and restart engine."""
        if self._engine:
            self._engine.reload()

    def _quit(self, icon, item):
        """Stop everything and exit."""
        self.stop()
        os._exit(0)


def main():
    """Entry point: run tray icon + engine."""
    TrayManager().start()


if __name__ == "__main__":
    main()
