from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from gui_utils import FONT_FAMILY, ColorButton
from gui_carga import VistaCarga
from gui_autoria import VistaProductividad, VistaEstadisticasAutoria, VistaTopAutores
from gui_geografia import VistaPaises, VistaUniversidades
from gui_impacto import VistaTrabajosCitados, VistaPromedioCitas, VistaTop10Trabajos
from gui_proyectos import VistaProyectos
from gui_exportar import VistaExportar

BG_APP = "#f5f5f5"
SIDEBAR = "#1e1e2e"
SIDEBAR_TEXT = "#e5e7eb"
SIDEBAR_MUTED = "#9ca3af"
ACCENT = "#7c3aed"
ACCENT_SOFT = "#4c1d95"
CARD = "#ffffff"
TEXT = "#111827"
MUTED = "#6b7280"
BORDER = "#e5e7eb"


class VistaBienvenida(tk.Frame):
    def __init__(self, parent: tk.Widget, app: "AppBibliometrico"):
        super().__init__(parent, bg=BG_APP)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        caja = tk.Frame(self, bg=BG_APP)
        caja.grid(row=0, column=0)

        tk.Label(caja, text="BIBLIOMÉTRICO", bg=BG_APP, fg=TEXT, font=(FONT_FAMILY, 28, "bold")).pack(pady=(0, 12))
        tk.Label(
            caja,
            text="Carga un archivo CSV de Scopus o Web of Science para comenzar",
            bg=BG_APP,
            fg=MUTED,
            font=(FONT_FAMILY, 12),
        ).pack(pady=(0, 24))
        ColorButton(
            caja,
            text="Cargar archivo CSV",
            command=lambda: self.app.cambiar_vista("carga"),
            bg=ACCENT,
            fg="white",
            relief="flat",
            activebackground="#6d28d9",
            cursor="hand2",
            font=(FONT_FAMILY, 12, "bold"),
            padx=24,
            pady=12,
        ).pack()


class AppBibliometrico(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BIBLIOMÉTRICO")
        self.geometry("1280x720")
        self.resizable(False, False)
        self.configure(bg=BG_APP)

        self.df = None
        self.nombre_archivo = None
        self.vistas = {}
        self.nav_buttons = {}
        self.current_view = None
        self.archivo_cargado = False

        self.export_selections: set = set()
        self.export_getters: dict = {}
        self.export_toggle_cbs: dict = {}

        self._configurar_estilos()
        self._crear_layout()
        self._crear_sidebar()
        self._crear_contenido()
        self._crear_barra_estado()

        self.deshabilitar_navegacion()
        self.cambiar_vista("bienvenida")

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure("Treeview", font=(FONT_FAMILY, 10), rowheight=28)
        estilo.configure("Treeview.Heading", font=(FONT_FAMILY, 10, "bold"))
        estilo.configure("TNotebook.Tab", padding=(12, 6), font=(FONT_FAMILY, 10, "bold"))

    def _crear_layout(self) -> None:
        self.body = tk.Frame(self, bg=BG_APP)
        self.body.pack(fill="both", expand=True)
        self.body.pack_propagate(False)

        self.sidebar = tk.Frame(self.body, bg=SIDEBAR, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.right_panel = tk.Frame(self.body, bg=BG_APP)
        self.right_panel.pack(side="left", fill="both", expand=True)
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        self.content = tk.Frame(self.right_panel, bg=BG_APP)
        self.content.grid(row=0, column=0, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

    def _crear_sidebar(self) -> None:
        # Logo fijo (no se desplaza)
        tk.Label(self.sidebar, text="BIBLIOMÉTRICO", bg=SIDEBAR, fg="white", font=(FONT_FAMILY, 16, "bold")).pack(anchor="w", padx=18, pady=(18, 6))
        tk.Label(self.sidebar, text="Análisis bibliométrico", bg=SIDEBAR, fg=SIDEBAR_MUTED, font=(FONT_FAMILY, 10)).pack(anchor="w", padx=18, pady=(0, 10))

        # Canvas scrollable para la navegación
        nav_canvas = tk.Canvas(self.sidebar, bg=SIDEBAR, highlightthickness=0)
        nav_canvas.pack(fill="both", expand=True)

        nav_inner = tk.Frame(nav_canvas, bg=SIDEBAR)
        nav_window = nav_canvas.create_window((0, 0), window=nav_inner, anchor="nw")

        def _on_nav_inner_configure(_e=None):
            nav_canvas.configure(scrollregion=nav_canvas.bbox("all"))

        def _on_nav_canvas_configure(e):
            nav_canvas.itemconfigure(nav_window, width=e.width)

        def _on_mousewheel(e):
            nav_canvas.yview_scroll(-1 * (e.delta // 120), "units")

        nav_inner.bind("<Configure>", _on_nav_inner_configure)
        nav_canvas.bind("<Configure>", _on_nav_canvas_configure)
        nav_canvas.bind("<MouseWheel>", _on_mousewheel)
        nav_inner.bind("<MouseWheel>", _on_mousewheel)

        secciones = [
            ("PROYECTOS", [("gestion_proyectos", "Gestion de proyectos")]),
            ("ARCHIVO", [("carga", "Cargar CSV")]),
            ("PRODUCTIVIDAD", [("productividad", "Métricas generales"), ("autoria", "Estadísticas de autoría"), ("top_autores", "Top 10 autores")]),
            ("GEOGRAFÍA", [("paises", "Lista de países"), ("universidades", "Universidades")]),
            ("IMPACTO", [("trabajos_citados", "Trabajos más citados"), ("promedio_citas", "Promedio anual de citas"), ("top_trabajos", "Top 10 trabajos")]),
            ("EXPORTAR", [("exportar", "Exportar reporte")]),
        ]

        for titulo, botones in secciones:
            tk.Label(nav_inner, text=titulo, bg=SIDEBAR, fg=SIDEBAR_MUTED, font=(FONT_FAMILY, 9, "bold")).pack(anchor="w", padx=18, pady=(10, 6))
            for nombre, texto in botones:
                boton = ColorButton(
                    nav_inner,
                    text=texto,
                    command=lambda n=nombre: self.cambiar_vista(n),
                    bg=SIDEBAR,
                    fg=SIDEBAR_TEXT,
                    relief="flat",
                    activebackground=ACCENT_SOFT,
                    activeforeground="white",
                    anchor="w",
                    cursor="hand2",
                    padx=18,
                    pady=10,
                    font=(FONT_FAMILY, 10),
                    disabledforeground="#6b7280",
                    borderwidth=0,
                )
                boton.pack(fill="x")
                boton.bind("<MouseWheel>", _on_mousewheel)
                self.nav_buttons[nombre] = boton

    def _crear_contenido(self) -> None:
        vistas = {
            "gestion_proyectos": VistaProyectos(self.content, self),
            "bienvenida": VistaBienvenida(self.content, self),
            "carga": VistaCarga(self.content, self),
            "productividad": VistaProductividad(self.content, self),
            "autoria": VistaEstadisticasAutoria(self.content, self),
            "top_autores": VistaTopAutores(self.content, self),
            "paises": VistaPaises(self.content, self),
            "universidades": VistaUniversidades(self.content, self),
            "trabajos_citados": VistaTrabajosCitados(self.content, self),
            "promedio_citas": VistaPromedioCitas(self.content, self),
            "top_trabajos": VistaTop10Trabajos(self.content, self),
            "exportar": VistaExportar(self.content, self),
        }
        for nombre, vista in vistas.items():
            vista.grid(row=0, column=0, sticky="nsew")
            self.vistas[nombre] = vista

    def _crear_barra_estado(self) -> None:
        barra = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        barra.pack(fill="x", side="bottom")
        self.lbl_archivo = tk.Label(barra, text="Sin archivo cargado", bg=CARD, fg=MUTED, font=(FONT_FAMILY, 10))
        self.lbl_archivo.pack(side="left", padx=16, pady=8)
        self.lbl_registros = tk.Label(barra, text="0 registros", bg=CARD, fg=MUTED, font=(FONT_FAMILY, 10, "bold"))
        self.lbl_registros.pack(side="right", padx=16, pady=8)

    def cambiar_vista(self, nombre_vista: str) -> None:
        vistas_siempre_activas = ["carga", "bienvenida", "gestion_proyectos"]
        if nombre_vista not in vistas_siempre_activas and not self.archivo_cargado:
            return

        vista = self.vistas[nombre_vista]
        vista.tkraise()
        self.current_view = nombre_vista
        self._actualizar_boton_activo(nombre_vista)
        if hasattr(vista, "on_show"):
            vista.on_show()

    def _actualizar_boton_activo(self, nombre_vista: str) -> None:
        for nombre, boton in self.nav_buttons.items():
            if str(boton.cget("state")) == "disabled":
                boton.configure(bg=SIDEBAR, fg="#6b7280")
                continue
            if nombre == nombre_vista:
                boton.configure(bg=ACCENT, fg="white", activebackground=ACCENT)
            else:
                boton.configure(bg=SIDEBAR, fg=SIDEBAR_TEXT, activebackground=ACCENT_SOFT)

    def toggle_exportacion(self, key: str) -> None:
        if key in self.export_selections:
            self.export_selections.discard(key)
            seleccionado = False
        else:
            self.export_selections.add(key)
            seleccionado = True
        for cb in self.export_toggle_cbs.get(key, []):
            cb(seleccionado)

    def registrar_toggle_cb(self, key: str, cb) -> None:
        self.export_toggle_cbs.setdefault(key, []).append(cb)

    def reset_export_state(self) -> None:
        keys = list(self.export_selections)
        self.export_selections.clear()
        self.export_getters.clear()
        for key in keys:
            for cb in self.export_toggle_cbs.get(key, []):
                cb(False)

    def actualizar_estado(self, nombre_archivo: str, total_registros: int) -> None:
        self.nombre_archivo = nombre_archivo
        self.archivo_cargado = True
        self.reset_export_state()
        self.lbl_archivo.configure(text=f"Archivo: {nombre_archivo}")
        self.lbl_registros.configure(text=f"{total_registros} registros")

    def habilitar_navegacion(self) -> None:
        self.archivo_cargado = True
        for nombre, boton in self.nav_buttons.items():
            boton.configure(state="normal")
            if nombre != self.current_view:
                boton.configure(bg=SIDEBAR, fg=SIDEBAR_TEXT)
        self._actualizar_boton_activo(self.current_view or "carga")

    def deshabilitar_navegacion(self) -> None:
        for nombre, boton in self.nav_buttons.items():
            if nombre in ["carga", "gestion_proyectos"]:
                boton.configure(state="normal", bg=SIDEBAR, fg=SIDEBAR_TEXT)
            else:
                boton.configure(state="disabled", bg=SIDEBAR, fg="#6b7280")


if __name__ == "__main__":
    app = AppBibliometrico()
    app.mainloop()