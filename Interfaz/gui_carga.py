from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, ttk

from gui_utils import FONT_FAMILY, ColorButton
from compat_imports import load_project_module

carga_mod = load_project_module("carga")
cargar_csv = carga_mod.cargar_csv

BG = "#f5f5f5"
CARD = "#ffffff"
TEXT = "#1f2937"
MUTED = "#6b7280"
SUCCESS = "#166534"
SUCCESS_BG = "#dcfce7"
ERROR = "#991b1b"
ERROR_BG = "#fee2e2"
WARN = "#92400e"
WARN_BG = "#fef3c7"
ACCENT = "#7c3aed"
BORDER = "#e5e7eb"


class VistaCarga(tk.Frame):
    def __init__(self, parent: tk.Widget, app: tk.Misc):
        super().__init__(parent, bg=BG)
        self.app = app
        self.detalles_visibles = False

        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._crear_encabezado()
        self._crear_formulario()
        self._crear_mensajes()
        self._crear_warning_panel()
        self._crear_preview()

    def _crear_encabezado(self) -> None:
        encabezado = tk.Frame(self, bg=BG)
        encabezado.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 8))
        encabezado.grid_columnconfigure(0, weight=1)

        tk.Label(
            encabezado,
            text="Cargar archivo CSV",
            bg=BG,
            fg=TEXT,
            font=(FONT_FAMILY, 20, "bold"),
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            encabezado,
            text="Importa un archivo exportado desde Scopus para habilitar el análisis.",
            bg=BG,
            fg=MUTED,
            font=(FONT_FAMILY, 10),
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

    def _crear_formulario(self) -> None:
        formulario = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        formulario.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        formulario.grid_columnconfigure(0, weight=1)

        tk.Label(
            formulario,
            text="Ruta del archivo",
            bg=CARD,
            fg=TEXT,
            font=(FONT_FAMILY, 10, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 6))

        fila = tk.Frame(formulario, bg=CARD)
        fila.grid(row=1, column=0, sticky="ew", padx=16)
        fila.grid_columnconfigure(0, weight=1)

        self.ruta_var = tk.StringVar()
        self.entry_ruta = tk.Entry(
            fila,
            textvariable=self.ruta_var,
            relief="solid",
            bd=1,
            highlightthickness=0,
            font=(FONT_FAMILY, 10),
        )
        self.entry_ruta.grid(row=0, column=0, sticky="ew", ipady=6)

        ColorButton(
            fila,
            text="Examinar",
            command=self.examinar_archivo,
            bg="#ede9fe",
            fg=ACCENT,
            relief="flat",
            activebackground="#ddd6fe",
            cursor="hand2",
            font=(FONT_FAMILY, 10, "bold"),
            padx=14,
            pady=6,
        ).grid(row=0, column=1, padx=(10, 0))

        acciones = tk.Frame(formulario, bg=CARD)
        acciones.grid(row=2, column=0, sticky="w", padx=16, pady=16)

        ColorButton(
            acciones,
            text="Cargar",
            command=self.ejecutar_carga,
            bg=ACCENT,
            fg="white",
            relief="flat",
            activebackground="#6d28d9",
            cursor="hand2",
            font=(FONT_FAMILY, 10, "bold"),
            padx=18,
            pady=8,
        ).pack(side="left")

        ColorButton(
            acciones,
            text="Limpiar",
            command=self.limpiar,
            bg="#f3f4f6",
            fg=TEXT,
            relief="flat",
            activebackground="#e5e7eb",
            cursor="hand2",
            font=(FONT_FAMILY, 10),
            padx=18,
            pady=8,
        ).pack(side="left", padx=(10, 0))

    def _crear_mensajes(self) -> None:
        self.mensaje_frame = tk.Frame(self, bg=BG)
        self.mensaje_frame.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 8))
        self.mensaje_frame.grid_columnconfigure(0, weight=1)

        self.mensaje_label = tk.Label(
            self.mensaje_frame,
            text="",
            bg=BG,
            fg=TEXT,
            justify="left",
            anchor="w",
            font=(FONT_FAMILY, 10),
            wraplength=780,
        )
        self.mensaje_label.grid(row=0, column=0, sticky="ew")

    def _crear_warning_panel(self) -> None:
        self.warning_panel = tk.Frame(self, bg=WARN_BG, highlightbackground="#f59e0b", highlightthickness=1)
        self.warning_panel.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 8))
        self.warning_panel.grid_columnconfigure(1, weight=1)
        self.warning_panel.grid_remove()

        self.toggle_btn = ColorButton(
            self.warning_panel,
            text="▶ Ver detalles",
            command=self.toggle_detalles,
            bg=WARN_BG,
            fg=WARN,
            relief="flat",
            activebackground=WARN_BG,
            activeforeground=WARN,
            cursor="hand2",
            font=(FONT_FAMILY, 10, "bold"),
            padx=4,
            pady=4,
        )
        self.toggle_btn.grid(row=0, column=0, sticky="w", padx=(12, 4), pady=10)

        self.warning_summary = tk.Label(
            self.warning_panel,
            text="",
            bg=WARN_BG,
            fg=WARN,
            font=(FONT_FAMILY, 10),
            justify="left",
            anchor="w",
            wraplength=720,
        )
        self.warning_summary.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=10)

        self.detalles_frame = tk.Frame(self.warning_panel, bg=WARN_BG)
        self.detalles_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 12))
        self.detalles_frame.grid_remove()

        self.detalles_label = tk.Label(
            self.detalles_frame,
            text="",
            bg=WARN_BG,
            fg=WARN,
            justify="left",
            anchor="w",
            font=(FONT_FAMILY, 10),
            wraplength=760,
        )
        self.detalles_label.pack(fill="x")

    def _crear_preview(self) -> None:
        contenedor = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        contenedor.grid(row=4, column=0, sticky="nsew", padx=24, pady=(0, 24))
        contenedor.grid_rowconfigure(1, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)

        tk.Label(
            contenedor,
            text="Vista previa",
            bg=CARD,
            fg=TEXT,
            font=(FONT_FAMILY, 12, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 8))

        tabla_frame = tk.Frame(contenedor, bg=CARD)
        tabla_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        tabla_frame.grid_rowconfigure(0, weight=1)
        tabla_frame.grid_columnconfigure(0, weight=1)

        self.preview_tree = ttk.Treeview(tabla_frame, show="headings", height=8)
        self.preview_tree.grid(row=0, column=0, sticky="nsew")

        scroll_y = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=scroll_y.set)
        scroll_y.grid(row=0, column=1, sticky="ns")

        scroll_x = ttk.Scrollbar(tabla_frame, orient="horizontal", command=self.preview_tree.xview)
        self.preview_tree.configure(xscrollcommand=scroll_x.set)
        scroll_x.grid(row=1, column=0, sticky="ew")

    def examinar_archivo(self) -> None:
        ruta = filedialog.askopenfilename(
            title="Selecciona un archivo CSV",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
        )
        if ruta:
            self.ruta_var.set(ruta)

    def ejecutar_carga(self) -> None:
        ruta = self.ruta_var.get().strip()
        if not ruta:
            self._mostrar_mensaje("Selecciona una ruta de archivo antes de cargar.", ERROR, ERROR_BG)
            return

        resultado = cargar_csv(ruta)
        self._limpiar_warning()
        self._limpiar_preview()

        if not resultado.get("ok"):
            self.app.df = None
            self.app.deshabilitar_navegacion()
            self.app.actualizar_estado("Sin archivo cargado", 0)

            error = resultado.get("error") or resultado.get("mensaje", "No se pudo cargar el archivo.")
            faltantes = resultado.get("faltantes_criticas", [])
            if faltantes:
                error += f"\nColumnas críticas faltantes: {', '.join(faltantes)}"
            self._mostrar_mensaje(error, ERROR, ERROR_BG)
            return

        self.app.df = resultado.get("dataframe")
        nombre_archivo = os.path.basename(ruta)
        self.app.actualizar_estado(nombre_archivo, resultado.get("total_registros", 0))
        self.app.habilitar_navegacion()

        self._mostrar_mensaje(
            f"✓ {resultado.get('mensaje', 'Archivo cargado correctamente')} · {resultado.get('total_registros', 0)} registros detectados.",
            SUCCESS,
            SUCCESS_BG,
        )

        self._mostrar_preview(resultado.get("preview", [])[:3])

        if resultado.get("faltantes_apa"):
            self._mostrar_warning(resultado)

    def _mostrar_mensaje(self, texto: str, fg: str, bg: str) -> None:
        self.mensaje_label.configure(text=texto, fg=fg, bg=bg)
        self.mensaje_frame.configure(bg=bg)

    def _mostrar_warning(self, resultado: dict) -> None:
        faltantes = resultado.get("faltantes_apa", [])
        metricas = resultado.get("metricas_incompletas", {})
        resumen = "Columnas APA faltantes: " + ", ".join(faltantes)
        self.warning_summary.configure(text=resumen)

        detalle_lineas = []
        for columna, metricas_afectadas in metricas.items():
            if columna not in faltantes:
                continue
            detalle_lineas.append(f"• {columna}: {', '.join(metricas_afectadas)}")
        if not detalle_lineas:
            detalle_lineas.append("• Algunas referencias APA y enlaces DOI quedarán incompletos.")
        self.detalles_label.configure(text="\n".join(detalle_lineas))
        self.detalles_visibles = False
        self.toggle_btn.configure(text="▶ Ver detalles")
        self.detalles_frame.grid_remove()
        self.warning_panel.grid()

    def toggle_detalles(self) -> None:
        self.detalles_visibles = not self.detalles_visibles
        if self.detalles_visibles:
            self.toggle_btn.configure(text="▼ Ocultar detalles")
            self.detalles_frame.grid()
        else:
            self.toggle_btn.configure(text="▶ Ver detalles")
            self.detalles_frame.grid_remove()

    def _mostrar_preview(self, preview: list[dict]) -> None:
        self._limpiar_preview()
        if not preview:
            return

        columnas = list(preview[0].keys())[:6]
        self.preview_tree["columns"] = columnas
        for columna in columnas:
            self.preview_tree.heading(columna, text=columna)
            self.preview_tree.column(columna, width=140, anchor="w")

        for fila in preview:
            valores = [str(fila.get(col, "")) for col in columnas]
            self.preview_tree.insert("", "end", values=valores)

    def _limpiar_preview(self) -> None:
        self.preview_tree.delete(*self.preview_tree.get_children())
        self.preview_tree["columns"] = ()

    def _limpiar_warning(self) -> None:
        self.warning_panel.grid_remove()
        self.detalles_frame.grid_remove()
        self.detalles_visibles = False
        self.toggle_btn.configure(text="▶ Ver detalles")
        self.warning_summary.configure(text="")
        self.detalles_label.configure(text="")

    def limpiar(self) -> None:
        self.ruta_var.set("")
        self._mostrar_mensaje("", TEXT, BG)
        self._limpiar_warning()
        self._limpiar_preview()

    def on_show(self) -> None:
        pass
