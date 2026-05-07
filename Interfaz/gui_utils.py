from __future__ import annotations

import sys
import tkinter as tk
from tkinter import ttk

if sys.platform == "win32":
    FONT_FAMILY = "Segoe UI"
elif sys.platform == "darwin":
    FONT_FAMILY = "Helvetica Neue"
else:
    FONT_FAMILY = "DejaVu Sans"

_ACCENT = "#7c3aed"
_BG = "#f5f5f5"
_CARD = "#ffffff"
_TEXT = "#1f2937"
_MUTED = "#6b7280"
_BORDER = "#e5e7eb"
_ROW_ALT = "#f9fafb"


def apply_theme(root: tk.Misc) -> None:
    """Aplica estilos ttk consistentes en macOS, Windows y Linux."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    # ── Treeview ──────────────────────────────────────────────────────────────
    style.configure(
        "Treeview",
        background=_CARD,
        foreground=_TEXT,
        fieldbackground=_CARD,
        font=(FONT_FAMILY, 10),
        rowheight=28,
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "Treeview.Heading",
        background=_BG,
        foreground=_TEXT,
        font=(FONT_FAMILY, 10, "bold"),
        relief="flat",
        borderwidth=0,
        padding=(8, 6),
    )
    style.map(
        "Treeview",
        background=[("selected", _ACCENT)],
        foreground=[("selected", "white")],
    )
    style.map(
        "Treeview.Heading",
        relief=[("active", "flat")],
        background=[("active", _BORDER)],
    )

    # ── Scrollbars — modernas sin flechas ───────────────────────────────────
    style.layout("Vertical.TScrollbar", [
        ("Vertical.Scrollbar.trough", {
            "sticky": "ns",
            "children": [
                ("Vertical.Scrollbar.thumb", {"sticky": "nswe", "expand": True})
            ],
        })
    ])
    style.layout("Horizontal.TScrollbar", [
        ("Horizontal.Scrollbar.trough", {
            "sticky": "ew",
            "children": [
                ("Horizontal.Scrollbar.thumb", {"sticky": "nswe", "expand": True})
            ],
        })
    ])
    style.configure("Vertical.TScrollbar",
                     width=8, troughcolor=_BORDER, background="#bfc5ce",
                     borderwidth=0, relief="flat")
    style.configure("Horizontal.TScrollbar",
                     width=8, troughcolor=_BORDER, background="#bfc5ce",
                     borderwidth=0, relief="flat")
    style.map("Vertical.TScrollbar",
              background=[("active", _MUTED), ("!active", "#bfc5ce")])
    style.map("Horizontal.TScrollbar",
              background=[("active", _MUTED), ("!active", "#bfc5ce")])

    # ── Notebook (tabs) ───────────────────────────────────────────────────────
    style.configure(
        "TNotebook",
        background=_BG,
        borderwidth=0,
        tabmargins=[0, 0, 0, 0],
    )
    style.configure(
        "TNotebook.Tab",
        background=_BORDER,
        foreground=_MUTED,
        font=(FONT_FAMILY, 10, "bold"),
        padding=[16, 8],
        borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", _CARD), ("active", "#f3f4f6")],
        foreground=[("selected", _TEXT), ("active", _TEXT)],
        expand=[("selected", [1, 1, 1, 0])],
    )


def setup_treeview_tags(tree: ttk.Treeview) -> None:
    """Configura zebra striping en un Treeview."""
    tree.tag_configure("odd", background=_CARD)
    tree.tag_configure("even", background=_ROW_ALT)


def insert_striped(tree: ttk.Treeview, row_index: int, values: tuple) -> None:
    tag = "even" if row_index % 2 == 0 else "odd"
    tree.insert("", "end", values=values, tags=(tag,))


def styled_entry(parent: tk.Widget, **kw) -> tk.Entry:
    """tk.Entry con colores explícitos — necesario para evitar fondo negro en macOS."""
    kw.setdefault("bg", _CARD)
    kw.setdefault("fg", _TEXT)
    kw.setdefault("insertbackground", _TEXT)
    kw.setdefault("disabledbackground", _BG)
    kw.setdefault("relief", "solid")
    kw.setdefault("bd", 1)
    kw.setdefault("highlightthickness", 0)
    return tk.Entry(parent, **kw)


def styled_listbox(parent: tk.Widget, **kw) -> tk.Listbox:
    """tk.Listbox con colores explícitos — necesario para evitar fondo negro en macOS."""
    kw.setdefault("bg", _CARD)
    kw.setdefault("fg", _TEXT)
    kw.setdefault("selectbackground", _ACCENT)
    kw.setdefault("selectforeground", "white")
    kw.setdefault("activestyle", "none")
    kw.setdefault("borderwidth", 0)
    kw.setdefault("highlightthickness", 0)
    return tk.Listbox(parent, **kw)


def bind_mousewheel(widget: tk.Widget, canvas: tk.Canvas) -> None:
    """Enlaza scroll del trackpad/mouse al canvas. Funciona en macOS, Windows y Linux."""
    if sys.platform == "darwin":
        def _scroll(e):
            canvas.yview_scroll(int(-1 * e.delta), "units")
        widget.bind("<MouseWheel>", _scroll)
    elif sys.platform == "win32":
        def _scroll(e):
            canvas.yview_scroll(-1 * (e.delta // 120), "units")
        widget.bind("<MouseWheel>", _scroll)
    else:
        widget.bind("<Button-4>", lambda _e: canvas.yview_scroll(-3, "units"))
        widget.bind("<Button-5>", lambda _e: canvas.yview_scroll(3, "units"))


def bind_mousewheel_recursive(widget: tk.Widget, canvas: tk.Canvas) -> None:
    """Igual que bind_mousewheel pero también aplica a todos los hijos actuales del widget.
    Necesario cuando el canvas contiene cards dinámicas cuyos hijos absorben los eventos."""
    bind_mousewheel(widget, canvas)
    for child in widget.winfo_children():
        bind_mousewheel_recursive(child, canvas)


def remove_maximize_button(window: tk.Tk) -> None:
    """Elimina el botón de maximizar grisado en Windows (no aplica en macOS/Linux)."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        GWL_STYLE = -16
        WS_MAXIMIZEBOX = 0x00010000
        SWP_FLAGS = 0x0027
        hwnd = ctypes.windll.user32.FindWindowW(None, window.title())
        if hwnd:
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style & ~WS_MAXIMIZEBOX)
            ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, SWP_FLAGS)
    except Exception:
        pass


class ColorButton(tk.Frame):
    """tk.Button replacement que respeta bg/fg en macOS y Linux."""

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
