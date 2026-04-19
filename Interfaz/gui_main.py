from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from gui_carga import VistaCarga
from gui_autoria import VistaProductividad, VistaEstadisticasAutoria, VistaTopAutores
from gui_geografia import VistaPaises, VistaUniversidades
from gui_impacto import VistaTrabajosCitados, VistaPromedioCitas, VistaTop10Trabajos

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

        tk.Label(caja, text="BIBLIOMÉTRICO", bg=BG_APP, fg=TEXT, font=("Segoe UI", 28, "bold")).pack(pady=(0, 12))
        tk.Label(
            caja,
            text="Carga un archivo CSV de Scopus o Web of Science para comenzar",
            bg=BG_APP,
            fg=MUTED,
            font=("Segoe UI", 12),
        ).pack(pady=(0, 24))
        tk.Button(
            caja,
            text="Cargar archivo CSV",
            command=lambda: self.app.cambiar_vista("carga"),
            bg=ACCENT,
            fg="white",
            relief="flat",
            activebackground="#6d28d9",
            cursor="hand2",
            font=("Segoe UI", 12, "bold"),
            padx=24,
            pady=12,
        ).pack()


class AppBibliometrico(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BIBLIOMÉTRICO")
        self.geometry("1100x680")
        self.resizable(False, False)
        self.configure(bg=BG_APP)

        self.df = None
        self.nombre_archivo = None
        self.vistas = {}
        self.nav_buttons = {}
        self.current_view = None
        self.archivo_cargado = False

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
        estilo.configure("Treeview", font=("Segoe UI", 10), rowheight=28)
        estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        estilo.configure("TNotebook.Tab", padding=(12, 6), font=("Segoe UI", 10, "bold"))

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
        tk.Label(self.sidebar, text="BIBLIOMÉTRICO", bg=SIDEBAR, fg="white", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=18, pady=(18, 6))
        tk.Label(self.sidebar, text="Análisis bibliométrico", bg=SIDEBAR, fg=SIDEBAR_MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=18, pady=(0, 16))

        secciones = [
            ("ARCHIVO", [("carga", "Cargar CSV")]),
            ("PRODUCTIVIDAD", [("productividad", "Métricas generales"), ("autoria", "Estadísticas de autoría"), ("top_autores", "Top 10 autores")]),
            ("GEOGRAFÍA", [("paises", "Lista de países"), ("universidades", "Universidades")]),
            ("IMPACTO", [("trabajos_citados", "Trabajos más citados"), ("promedio_citas", "Promedio anual de citas"), ("top_trabajos", "Top 10 trabajos")]),
        ]

        for titulo, botones in secciones:
            tk.Label(self.sidebar, text=titulo, bg=SIDEBAR, fg=SIDEBAR_MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=18, pady=(10, 6))
            for nombre, texto in botones:
                boton = tk.Button(
                    self.sidebar,
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
                    font=("Segoe UI", 10),
                    disabledforeground="#6b7280",
                    borderwidth=0,
                )
                boton.pack(fill="x")
                self.nav_buttons[nombre] = boton

    def _crear_contenido(self) -> None:
        vistas = {
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
        }
        for nombre, vista in vistas.items():
            vista.grid(row=0, column=0, sticky="nsew")
            self.vistas[nombre] = vista

    def _crear_barra_estado(self) -> None:
        barra = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        barra.pack(fill="x", side="bottom")
        self.lbl_archivo = tk.Label(barra, text="Sin archivo cargado", bg=CARD, fg=MUTED, font=("Segoe UI", 10))
        self.lbl_archivo.pack(side="left", padx=16, pady=8)
        self.lbl_registros = tk.Label(barra, text="0 registros", bg=CARD, fg=MUTED, font=("Segoe UI", 10, "bold"))
        self.lbl_registros.pack(side="right", padx=16, pady=8)

    def cambiar_vista(self, nombre_vista: str) -> None:
        if nombre_vista != "carga" and nombre_vista != "bienvenida" and not self.archivo_cargado:
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

    def actualizar_estado(self, nombre_archivo: str, total_registros: int) -> None:
        self.nombre_archivo = nombre_archivo
        self.archivo_cargado = True
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
            if nombre == "carga":
                boton.configure(state="normal")
            else:
                boton.configure(state="disabled", bg=SIDEBAR, fg="#6b7280")


if __name__ == "__main__":
    app = AppBibliometrico()
    app.mainloop()
