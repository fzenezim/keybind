# keybind

Configurable global hotkeys for Windows that type text or open links.

## Features

- **Global hotkeys**: 2-5 key combinations, captured via pynput
- **Text injection**: type any text string at the current cursor position
- **URL shortcuts**: open a link in the default browser
- **Persistent config**: shortcuts saved to `%APPDATA%\keybind.json`
- **GUI editor**: tkinter-based interface with add/remove rows
- **Live reload**: engine picks up config changes without restart
- **Conflict warning**: duplicate key combos trigger a confirmation dialog on save
- **System tray**: run headless from the tray with right-click menu (Open Config / Reload / Exit)
- **Standalone exe**: build a `keybind.exe` with PyInstaller (no Python required)

## Installation

```bash
git clone https://github.com/fzenezim/keybind.git
cd keybind
py -V:3.14 -m venv .venv
.venv/Scripts/pip install -e ".[dev]"
```

## Usage

### System tray (recommended)

```bash
.venv/Scripts/keybind-tray
```

Opens a tray icon with a right-click menu: Open Config, Reload, Exit.

### GUI (configure shortcuts)

```bash
.venv/Scripts/keybind
# or
.venv/Scripts/python -m keybind
```

### Headless engine (run in background)

```bash
.venv/Scripts/keybind-core
```

Or start the GUI / tray — they run the engine automatically.

## Conflict handling

If two enabled shortcuts share the same key combo, the GUI shows a
confirmation dialog on **Save** listing the conflicting shortcuts. The first
shortcut in the list takes priority. Disabling one of them (uncheck the box)
resolves the conflict without deleting anything.

## Building the exe

```bash
.venv/Scripts/python -m PyInstaller keybind.spec --noconfirm
```

Output: `dist/keybind.exe` (single file, no console window).

## Configuration

Shortcuts are stored in `%APPDATA%\keybind.json`:

```json
{
  "shortcuts": [
    {
      "combo": ["ctrl", "shift", "f"],
      "action": {"text": "Hello, world!", "is_link": false, "url": ""},
      "enabled": true
    }
  ]
}
```

## Development

```bash
.venv/Scripts/python -m pytest tests/ -v
```

CI runs on every push/PR (GitHub Actions, Windows runners, Python 3.12/3.13).

## License

MIT
