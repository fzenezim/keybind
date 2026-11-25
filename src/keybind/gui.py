"""Tkinter GUI for configuring keybind shortcuts."""

import tkinter as tk
import threading
import os

from .data_model import Config, KeyCombo, Shortcut, ShortcutAction


def main():
    """Entry point for the keybind GUI."""
    root = tk.Tk()
    app = KeybindApp(root)
    root.mainloop()


class KeybindApp:
    """Main application window for managing keybind shortcuts."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Keybind - Global Hotkeys")
        self.root.geometry("640x420")
        self.root.minsize(520, 320)

        self.config = Config.load()
        self._engine = None
        self._row_widgets = []
        self._start_engine()
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _start_engine(self):
        from .engine import KeybindEngine
        self._engine = KeybindEngine(config_loader=lambda: self.config)
        t = threading.Thread(target=self._engine.start, daemon=True)
        t.start()

    def _build_ui(self):
        # Title bar
        title_frame = tk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        tk.Label(
            title_frame,
            text="Keybind",
            font=("Segoe UI", 16, "bold"),
        ).pack(side=tk.LEFT)
        self._status_label = tk.Label(
            title_frame,
            text="",
            fg="gray",
            font=("Segoe UI", 9),
        )
        self._status_label.pack(side=tk.RIGHT)

        # Shortcut rows container (scrollable)
        rows_frame = tk.Frame(self.root)
        rows_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        canvas = tk.Canvas(rows_frame, highlightthickness=0)
        scrollbar = tk.Scrollbar(rows_frame, orient=tk.VERTICAL, command=canvas.yview)
        self._rows_inner = tk.Frame(canvas)
        self._rows_inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self._rows_inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Populate rows
        for i, sc in enumerate(self.config.shortcuts):
            self._add_row_widget(sc, index=i)

        # Add button
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        tk.Button(
            btn_frame,
            text="+ Add shortcut",
            command=self._on_add_shortcut,
        ).pack(side=tk.LEFT)

        tk.Button(
            btn_frame,
            text="Save",
            command=self._on_save,
        ).pack(side=tk.RIGHT)

    def _add_row_widget(self, shortcut: Shortcut, index: int):
        """Add a visual row for a shortcut to the inner frame."""
        row = tk.Frame(self._rows_inner)
        row.pack(fill=tk.X, pady=3)

        # Enabled checkbox
        chk_var = tk.BooleanVar(value=shortcut.enabled)
        tk.Checkbutton(row, variable=chk_var, width=1).pack(side=tk.LEFT, padx=(2, 4))

        # Key combo widgets
        keys_frame = tk.Frame(row)
        keys_frame.pack(side=tk.LEFT, padx=(0, 6))

        key_entries = []
        for key_name in shortcut.combo.keys:
            entry = tk.Entry(keys_frame, width=6, font=("Consolas", 9))
            entry.insert(0, key_name)
            entry.config(state="readonly")
            key_entries.append(entry)
            entry.pack(side=tk.LEFT, padx=1)

        def add_key():
            if len(key_entries) < 5:
                e = tk.Entry(keys_frame, width=6, font=("Consolas", 9))
                e.pack(side=tk.LEFT, padx=1)
                key_entries.append(e)
                e.focus_set()

        def remove_key():
            if len(key_entries) > 2:
                last = key_entries.pop()
                last.destroy()

        tk.Button(keys_frame, text="+", width=2, command=add_key).pack(side=tk.LEFT, padx=(2, 0))
        tk.Button(keys_frame, text="-", width=2, command=remove_key).pack(side=tk.LEFT, padx=(0, 4))

        # Action area
        action_frame = tk.Frame(row)
        action_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        is_link_var = tk.BooleanVar(value=shortcut.action.is_link)
        text_var = tk.StringVar(value=shortcut.action.text)
        url_var = tk.StringVar(value=shortcut.action.url)

        text_entry = tk.Entry(action_frame, textvariable=text_var)
        text_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        url_entry = tk.Entry(action_frame, textvariable=url_var)
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def toggle_link():
            if is_link_var.get():
                text_entry.config(state="disabled")
                url_entry.config(state="normal")
            else:
                text_entry.config(state="normal")
                url_entry.config(state="disabled")

        link_chk = tk.Checkbutton(action_frame, text="URL", variable=is_link_var, command=toggle_link)
        link_chk.pack(side=tk.LEFT, padx=(4, 0))
        toggle_link()

        # Delete row button
        def delete_row():
            if len(self.config.shortcuts) <= 1:
                self._status_label.config(text="Cannot delete the last shortcut", fg="red")
                return
            self.config.remove_shortcut(index)
            self._refresh_rows()
            self._status_label.config(text="Shortcut deleted", fg="orange")

        tk.Button(row, text="Delete", width=6, command=delete_row).pack(side=tk.RIGHT, padx=(4, 0))

        self._row_widgets.append({
            "frame": row,
            "chk_var": chk_var,
            "key_entries": key_entries,
            "text_var": text_var,
            "url_var": url_var,
            "is_link_var": is_link_var,
            "shortcut": shortcut,
        })

    def _refresh_rows(self):
        """Rebuild all row widgets from config."""
        for w in self._row_widgets:
            w["frame"].destroy()
        self._row_widgets = []
        for i, sc in enumerate(self.config.shortcuts):
            self._add_row_widget(sc, index=i)

    def _collect_rows_to_config(self):
        """Read UI state back into config."""
        for i, w in enumerate(self._row_widgets):
            if i >= len(self.config.shortcuts):
                break
            sc = self.config.shortcuts[i]
            sc.enabled = w["chk_var"].get()
            sc.action.is_link = w["is_link_var"].get()
            sc.action.text = w["text_var"].get().strip()
            sc.action.url = w["url_var"].get().strip()
            keys = [e.get().strip().lower() for e in w["key_entries"] if e.get().strip()]
            if len(keys) >= 2:
                sc.combo = KeyCombo(keys=keys)

    def _on_add_shortcut(self):
        """Add a new shortcut row."""
        self.config.add_shortcut(Shortcut(combo=KeyCombo(keys=["ctrl", "shift"])))
        self._refresh_rows()
        self._status_label.config(text="Added new shortcut", fg="green")

    def _on_save(self):
        """Save config and reload engine."""
        self._collect_rows_to_config()
        self.config.save()
        if self._engine:
            self._engine.reload()
        self._status_label.config(text="Saved & applied", fg="green")

    def _on_close(self):
        """Cleanup on window close."""
        if self._engine:
            self._engine.stop()
        self._collect_rows_to_config()
        self.config.save()
        self.root.destroy()
