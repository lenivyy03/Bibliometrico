from __future__ import annotations

import sys
import tkinter as tk

if sys.platform == "win32":
    FONT_FAMILY = "Segoe UI"
elif sys.platform == "darwin":
    FONT_FAMILY = "Helvetica Neue"
else:
    FONT_FAMILY = "DejaVu Sans"


class ColorButton(tk.Frame):
    """tk.Button replacement that respects bg/fg on macOS and Linux."""

    def __init__(
        self,
        parent: tk.Widget,
        text: str = "",
        command=None,
        bg: str = "#ffffff",
        fg: str = "#000000",
        activebackground: str | None = None,
        activeforeground: str | None = None,
        disabledforeground: str = "#9ca3af",
        cursor: str = "hand2",
        font=None,
        padx: int = 8,
        pady: int = 4,
        anchor: str = "center",
        width: int = 0,
        **_ignored,
    ):
        super().__init__(parent, bg=bg, cursor=cursor, borderwidth=0, relief="flat")
        self._bg = bg
        self._fg = fg
        self._active_bg = activebackground if activebackground is not None else bg
        self._active_fg = activeforeground if activeforeground is not None else fg
        self._disabled_fg = disabledforeground
        self._command = command
        self._state = "normal"

        lbl_kw: dict = dict(bg=bg, fg=fg, padx=padx, pady=pady, anchor=anchor, cursor=cursor)
        if font is not None:
            lbl_kw["font"] = font
        if width:
            lbl_kw["width"] = width
        self._label = tk.Label(self, text=text, **lbl_kw)
        self._label.pack(fill="both", expand=True)

        for w in (self, self._label):
            w.bind("<Button-1>", self._on_click)
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)

    def _on_click(self, _event=None):
        if self._state == "normal" and self._command:
            self._command()

    def _on_enter(self, _event=None):
        if self._state == "normal":
            super().configure(bg=self._active_bg)
            self._label.configure(bg=self._active_bg, fg=self._active_fg)

    def _on_leave(self, _event=None):
        if self._state == "normal":
            super().configure(bg=self._bg)
            self._label.configure(bg=self._bg, fg=self._fg)

    def configure(self, **kw):
        if "command" in kw:
            self._command = kw.pop("command")
        if "activebackground" in kw:
            self._active_bg = kw.pop("activebackground")
        if "activeforeground" in kw:
            self._active_fg = kw.pop("activeforeground")

        state = kw.pop("state", None)
        bg = kw.pop("bg", kw.pop("background", None))
        fg = kw.pop("fg", kw.pop("foreground", None))

        if state is not None:
            self._state = state
            if state == "disabled":
                super().configure(cursor="")
                self._label.configure(cursor="")
            else:
                super().configure(cursor="hand2")
                self._label.configure(cursor="hand2")
                if fg is None:
                    self._label.configure(fg=self._fg)

        if bg is not None:
            self._bg = bg
            super().configure(bg=bg)
            self._label.configure(bg=bg)

        if fg is not None:
            self._fg = fg
            self._label.configure(fg=fg)

        label_keys = {"text", "font", "padx", "pady", "anchor", "width"}
        label_kw = {k: v for k, v in kw.items() if k in label_keys}
        if label_kw:
            self._label.configure(**label_kw)

    config = configure

    def cget(self, key: str):
        if key == "state":
            return self._state
        if key in ("bg", "background"):
            return self._bg
        if key in ("fg", "foreground"):
            return self._fg
        if key == "text":
            return self._label.cget("text")
        return super().cget(key)
