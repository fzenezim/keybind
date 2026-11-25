"""Core entry point: runs the hotkey engine as a background process."""

import os
import sys
import time


def main():
    """Run the engine in a loop, reloading config on file change."""
    from .data_model import Config
    from .engine import KeybindEngine

    appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
    config_path = os.path.join(appdata, "keybind.json")

    engine = KeybindEngine(config_loader=lambda: Config.load(config_path))
    engine.start()

    try:
        last_mtime = os.path.getmtime(config_path)
    except OSError:
        last_mtime = 0.0

    print("keybind engine running (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(0.5)
            try:
                current_mtime = os.path.getmtime(config_path)
                if current_mtime != last_mtime:
                    last_mtime = current_mtime
                    engine.reload()
            except OSError:
                pass
    except KeyboardInterrupt:
        engine.stop()
        print("keybind engine stopped")


if __name__ == "__main__":
    main()
