"""Tests for keybind.data_model conflict detection."""

from keybind.data_model import Config, KeyCombo, Shortcut, ShortcutAction


def test_no_conflicts_different_combos():
    cfg = Config(shortcuts=[
        Shortcut(combo=KeyCombo(keys=["ctrl", "shift", "f"]), action=ShortcutAction(text="a")),
        Shortcut(combo=KeyCombo(keys=["ctrl", "alt", "g"]), action=ShortcutAction(text="b")),
    ])
    assert cfg.find_combo_conflicts() == []


def test_conflict_same_combo():
    cfg = Config(shortcuts=[
        Shortcut(combo=KeyCombo(keys=["ctrl", "shift", "f"]), action=ShortcutAction(text="a")),
        Shortcut(combo=KeyCombo(keys=["ctrl", "shift", "f"]), action=ShortcutAction(text="b")),
    ])
    conflicts = cfg.find_combo_conflicts()
    assert len(conflicts) == 1
    combo_str, idxs = conflicts[0]
    assert idxs == [0, 1]


def test_conflict_ignores_disabled():
    cfg = Config(shortcuts=[
        Shortcut(combo=KeyCombo(keys=["ctrl", "shift", "f"]), action=ShortcutAction(text="a"), enabled=True),
        Shortcut(combo=KeyCombo(keys=["ctrl", "shift", "f"]), action=ShortcutAction(text="b"), enabled=False),
    ])
    assert cfg.find_combo_conflicts() == []


def test_conflict_case_insensitive():
    cfg = Config(shortcuts=[
        Shortcut(combo=KeyCombo(keys=["Ctrl", "Shift", "F"]), action=ShortcutAction(text="a")),
        Shortcut(combo=KeyCombo(keys=["ctrl", "shift", "f"]), action=ShortcutAction(text="b")),
    ])
    conflicts = cfg.find_combo_conflicts()
    assert len(conflicts) == 1


def test_multiple_conflicts():
    cfg = Config(shortcuts=[
        Shortcut(combo=KeyCombo(keys=["ctrl", "shift", "f"]), action=ShortcutAction(text="a")),
        Shortcut(combo=KeyCombo(keys=["ctrl", "shift", "f"]), action=ShortcutAction(text="b")),
        Shortcut(combo=KeyCombo(keys=["alt", "f1"]), action=ShortcutAction(text="c")),
        Shortcut(combo=KeyCombo(keys=["alt", "f1"]), action=ShortcutAction(text="d")),
        Shortcut(combo=KeyCombo(keys=["win", "k"]), action=ShortcutAction(text="e")),
    ])
    conflicts = cfg.find_combo_conflicts()
    assert len(conflicts) == 2
