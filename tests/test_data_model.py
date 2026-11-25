"""Tests for keybind.data_model."""

import json
import os
import tempfile
import pytest
from keybind.data_model import Config, KeyCombo, Shortcut, ShortcutAction


def test_key_combo_to_str():
    kc = KeyCombo(keys=["ctrl", "shift", "f"])
    assert kc.to_str() == "ctrl+shift+f"


def test_key_combo_to_tuple():
    kc = KeyCombo(keys=["ctrl", "alt", "x"])
    assert kc.to_tuple() == ("ctrl", "alt", "x")


def test_shortcut_action_text_valid():
    sa = ShortcutAction(text="hello")
    assert sa.is_valid


def test_shortcut_action_link_valid():
    sa = ShortcutAction(is_link=True, url="https://example.com")
    assert sa.is_valid


def test_shortcut_action_empty_text_invalid():
    sa = ShortcutAction(text="")
    assert not sa.is_valid


def test_shortcut_action_empty_url_invalid():
    sa = ShortcutAction(is_link=True, url="")
    assert not sa.is_valid


def test_shortcut_to_dict_roundtrip():
    sc = Shortcut(
        combo=KeyCombo(keys=["ctrl", "shift", "f"]),
        action=ShortcutAction(text="hello"),
        enabled=True,
    )
    d = sc.to_dict()
    sc2 = Shortcut.from_dict(d)
    assert sc2.combo.keys == ["ctrl", "shift", "f"]
    assert sc2.action.text == "hello"
    assert sc2.enabled is True


def test_config_save_and_load(tmp_path):
    p = str(tmp_path / "test_keybind.json")
    cfg = Config(shortcuts=[
        Shortcut(combo=KeyCombo(keys=["ctrl", "shift"]), action=ShortcutAction(text="hi")),
    ])
    cfg.save(p)

    cfg2 = Config.load(p)
    assert len(cfg2.shortcuts) == 1
    assert cfg2.shortcuts[0].action.text == "hi"


def test_config_load_missing_file():
    cfg = Config.load("/nonexistent/path/keybind.json")
    assert len(cfg.shortcuts) == 1  # default


def test_config_load_corrupt_file(tmp_path):
    p = str(tmp_path / "corrupt.json")
    with open(p, "w") as f:
        f.write("not valid json {{{")
    cfg = Config.load(p)
    assert len(cfg.shortcuts) == 1  # fallback to default


def test_config_add_remove_shortcut():
    cfg = Config(shortcuts=[])
    sc = Shortcut(combo=KeyCombo(keys=["ctrl", "shift"]))
    cfg.add_shortcut(sc)
    assert len(cfg.shortcuts) == 1
    cfg.remove_shortcut(0)
    assert len(cfg.shortcuts) == 0


def test_config_get_enabled_shortcuts():
    cfg = Config(shortcuts=[
        Shortcut(combo=KeyCombo(keys=["ctrl", "shift"]), enabled=True),
        Shortcut(combo=KeyCombo(keys=["alt", "f"]), enabled=False),
    ])
    enabled = cfg.get_enabled_shortcuts()
    assert len(enabled) == 1
    assert enabled[0].combo.keys == ["ctrl", "shift"]
