"""Data model and configuration persistence for keybind."""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional


def _config_path() -> str:
    """Return the path to the config file, using a fixed name under %APPDATA%."""
    appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
    return os.path.join(appdata, "keybind.json")


@dataclass
class KeyCombo:
    """A single hotkey combination: 2-5 keys."""
    keys: list  # list of key names in order, e.g. ["ctrl", "shift", "f"]

    def to_tuple(self) -> tuple:
        return tuple(self.keys)

    def to_str(self) -> str:
        return "+".join(self.keys)


@dataclass
class ShortcutAction:
    """The action to perform: type text or open a URL."""
    text: str = ""
    is_link: bool = False
    url: str = ""

    @property
    def is_valid(self) -> bool:
        if self.is_link:
            return bool(self.url.strip())
        return bool(self.text.strip())


@dataclass
class Shortcut:
    """A configurable shortcut: combo + action."""
    combo: KeyCombo
    action: ShortcutAction = field(default_factory=ShortcutAction)
    enabled: bool = True

    def to_dict(self) -> dict:
        return {
            "combo": self.combo.keys,
            "action": asdict(self.action),
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Shortcut":
        return cls(
            combo=KeyCombo(keys=d["combo"]),
            action=ShortcutAction(**d["action"]),
            enabled=d.get("enabled", True),
        )


@dataclass
class Config:
    """Top-level configuration: list of shortcuts."""
    shortcuts: list = field(default_factory=list)

    @classmethod
    def load(cls, path: Optional[str] = None) -> "Config":
        """Load config from JSON file, or return default config if missing."""
        p = path or _config_path()
        if not os.path.exists(p):
            return cls(shortcuts=[Shortcut(combo=KeyCombo(keys=["ctrl", "shift"]))])
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            shortcuts = [Shortcut.from_dict(d) for d in data.get("shortcuts", [])]
            return cls(shortcuts=shortcuts)
        except (json.JSONDecodeError, KeyError, TypeError):
            return cls(shortcuts=[Shortcut(combo=KeyCombo(keys=["ctrl", "shift"]))])

    def save(self, path: Optional[str] = None) -> None:
        """Save config to JSON file."""
        p = path or _config_path()
        data = {"shortcuts": [s.to_dict() for s in self.shortcuts]}
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_shortcut(self, shortcut: Shortcut) -> None:
        self.shortcuts.append(shortcut)

    def remove_shortcut(self, index: int) -> None:
        if 0 <= index < len(self.shortcuts):
            self.shortcuts.pop(index)

    def get_enabled_shortcuts(self) -> list:
        return [s for s in self.shortcuts if s.enabled]
