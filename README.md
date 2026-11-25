# keybind

Configurable global hotkeys for Windows that type text or open links.

## Features

- **Global hotkeys**: 2-5 key combinations, captured via pynput
- **Text injection**: type any text string at the current cursor position
- **URL shortcuts**: open a link in the default browser
- **Persistent config**: shortcuts saved to `%APPDATA%\keybind.json`
- **GUI editor**: tkinter-based interface with add/remove rows
- **Live reload**: engine picks up config changes without restart

## Installation

```bash
git clone https://github.com/fzenezim/keybind.git
cd keybind
py -V:3.14 -m venv .venv
.venv/Scripts/pip install -e ".[dev]"
```

## Usage

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

Or start the GUI — it runs the engine automatically in the background.

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

## License

MIT
