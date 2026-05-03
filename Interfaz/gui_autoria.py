from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from gui_utils import FONT_FAMILY, ColorButton
from compat_imports import load_project_module

conteo_mod = load_project_module("conteo")
estad_mod = load_project_module("estadisticas_autoria")
filtrado_mod = load_project_module("filtrado")
load_project_module("impacto")
tops_mod = load_project_module("tops")

metricas_prod = conteo_mod.metricas_prod
num_minimo_autores = estad_mod.num_minimo_autores
num_maximo_autores = estad_mod.num_maximo_autores
num_promedio_autores = estad_mod.num_promedio_autores
tabla_comparativa_autoria = filtrado_mod.tabla_comparativa_autoria
top_autores = tops_mod.top_autores

BG = "#f5f5f5"
CARD = "#ffffff"
TEXT = "#1f2937"
MUTED = "#6b7280"
ACCENT = "#7c3aed"
BORDER = "#e5e7eb"
ERROR = "#991b1b"


class TarjetaMetrica(tk.Frame):
    def __init__(self, parent: tk.Widget, titulo: str):
        super().__init__(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        self.grid_columnconfigure(0, weight=1)
        self.valor = tk.Label(self, text="—", bg=CARD, fg=TEXT, font=(FONT_FAMILY, 24, "bold"))
        self.valor.grid(row=0, column=0, padx=18, pady=(14, 2))
        self.titulo = tk.Label(self, text=titulo, bg=CARD, fg=MUTED, font=(FONT_FAMILY, 10))
        self.titulo.grid(row=1, column=0, padx=18, pady=(0, 14))

    def actualizar(self, valor: str) -> None:
        self.valor.configure(text=valor)


class _BaseVistaDatos(tk.Frame):
    def __init__(self, parent: tk.Widget, app: tk.Misc, titulo: str):
        super().__init__(parent, bg=BG)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._crear_header(titulo)

    def _crear_header(self, titulo: str) -> None:
        head = tk.Frame(self, bg=BG)
        head.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 10))
        head.grid_columnconfigure(0, weight=1)
        tk.Label(head, text=titulo, bg=BG, fg=TEXT, font=(FONT_FAMILY, 20, "bold")).grid(row=0, column=0, sticky="w")
        self.btn_actualizar = ColorButton(
            head,
            text="Actualizar",
            bg="#ede9fe",
            fg=ACCENT,
            relief="flat",
            activebackground="#ddd6fe",
            cursor="hand2",
            font=(FONT_FAMILY, 10, "bold"),
            padx=14,
            pady=8,
        )
        self.btn_actualizar.grid(row=0, column=1, sticky="e")

        self.status_label = tk.Label(head, text="", bg=BG, fg=MUTED, font=(FONT_FAMILY, 10))
        self.status_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

        self.error_label = tk.Label(head, text="", bg=BG, fg=ERROR, font=(FONT_FAMILY, 10), wraplength=780, justify="left")
        self.error_label.grid(row=2, column=0, columnspan=2, sticky="w")

    def _set_status(self, texto: str = "") -> None:
        self.status_label.configure(text=texto)

    def _set_error(self, texto: str = "") -> None:
        self.error_label.configure(text=texto)

    def _verificar_df(self) -> bool:
        if self.app.df is None or getattr(self.app.df, "empty", False):
            self._set_error("No hay un archivo cargado todavía.")
            return False
        return True


class VistaProductividad(_BaseVistaDatos):
    def __init__(self, parent: tk.Widget, app: tk.Misc):
        super().__init__(parent, app, "Métricas generales")
        self.btn_actualizar.configure(command=self.cargar_datos)

        tarjetas = tk.Frame(self, bg=BG)
        tarjetas.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 10))
        for i in range(3):
            tarjetas.grid_columnconfigure(i, weight=1)

        self.card_total = TarjetaMetrica(tarjetas, "Total de publicaciones")
        self.card_total.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.card_autores = TarjetaMetrica(tarjetas, "Autores únicos")
        self.card_autores.grid(row=0, column=1, sticky="ew", padx=5)
        self.card_unico = TarjetaMetrica(tarjetas, "Artículos de un solo autor")
        self.card_unico.grid(row=0, column=2, sticky="ew", padx=(10, 0))

        info = tk.Label(
            self,
            text="Resumen consolidado de productividad para el archivo cargado.",
            bg=BG,
            fg=MUTED,
            font=(FONT_FAMILY, 10),
        )
        info.grid(row=2, column=0, sticky="nw", padx=24, pady=(8, 0))

    def cargar_datos(self) -> None:
        self._set_error("")
        if not self._verificar_df():
            self.card_total.actualizar("—")
            self.card_autores.actualizar("—")
            self.card_unico.actualizar("—")
            return
        self._set_status("Calculando…")
        self.after(10, self._calcular)

    def _calcular(self) -> None:
        try:
            metricas = metricas_prod(self.app.df)
            self.card_total.actualizar(str(metricas.get("Total de publicaciones", 0)))
            self.card_autores.actualizar(str(metricas.get("Autores únicos", 0)))
            self.card_unico.actualizar(str(metricas.get("Artículos de un solo autor", 0)))
            self._set_status("Datos actualizados.")
        except Exception as exc:
            self._set_error(f"No se pudieron calcular las métricas: {exc}")
            self._set_status("")

    def on_show(self) -> None:
        if self.app.df is not None:
            self.cargar_datos()


class VistaEstadisticasAutoria(_BaseVistaDatos):
    def __init__(self, parent: tk.Widget, app: tk.Misc):
        super().__init__(parent, app, "Estadísticas de autoría")
        self.btn_actualizar.configure(command=self.cargar_datos)
        self._tabla_completa = None

        tarjetas = tk.Frame(self, bg=BG)
        tarjetas.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 10))
        for i in range(3):
            tarjetas.grid_columnconfigure(i, weight=1)

        self.card_min = TarjetaMetrica(tarjetas, "Mínimo de autores")
        self.card_min.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.card_max = TarjetaMetrica(tarjetas, "Máximo de autores")
        self.card_max.grid(row=0, column=1, sticky="ew", padx=5)
        self.card_prom = TarjetaMetrica(tarjetas, "Promedio de autores")
        self.card_prom.grid(row=0, column=2, sticky="ew", padx=(10, 0))

        cuerpo = tk.Frame(self, bg=BG)
        cuerpo.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 24))
        cuerpo.grid_rowconfigure(2, weight=1)
        cuerpo.grid_columnconfigure(0, weight=1)

        filtro = tk.Frame(cuerpo, bg=BG)
        filtro.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        filtro.grid_columnconfigure(1, weight=1)
        tk.Label(filtro, text="Buscar institución:", bg=BG, fg=TEXT, font=(FONT_FAMILY, 10, "bold")).grid(row=0, column=0, sticky="w")
        self.busqueda_var = tk.StringVar()
        self.busqueda_var.trace_add("write", lambda *_: self.aplicar_filtro())
        tk.Entry(filtro, textvariable=self.busqueda_var, relief="solid", bd=1, highlightthickness=0).grid(row=0, column=1, sticky="ew", padx=(10, 0), ipady=6)

        tabla_card = tk.Frame(cuerpo, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        tabla_card.grid(row=2, column=0, sticky="nsew")
        tabla_card.grid_rowconfigure(0, weight=1)
        tabla_card.grid_columnconfigure(0, weight=1)

        columnas = (
            "Universidad_Institucion",
            "Total_Articulos",
            "Promedio_Autores",
            "Maximo_Autores",
            "Total_Individuales",
            "Total_Colaborativos",
        )
        self.tree = ttk.Treeview(tabla_card, columns=columnas, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")

        encabezados = {
            "Universidad_Institucion": "Institución",
            "Total_Articulos": "Artículos",
            "Promedio_Autores": "Promedio",
            "Maximo_Autores": "Máximo",
            "Total_Individuales": "Individuales",
            "Total_Colaborativos": "Colaborativos",
        }
        for col in columnas:
            ancho = 280 if col == "Universidad_Institucion" else 110
            self.tree.heading(col, text=encabezados[col])
            self.tree.column(col, width=ancho, anchor="w")

        scroll = ttk.Scrollbar(tabla_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

    def cargar_datos(self) -> None:
        self._set_error("")
        if not self._verificar_df():
            return
        self._set_status("Calculando…")
        self.after(10, self._calcular)

    def _calcular(self) -> None:
        try:
            minimo = num_minimo_autores(self.app.df)
            maximo = num_maximo_autores(self.app.df)
            promedio = num_promedio_autores(self.app.df)
            tabla = tabla_comparativa_autoria(self.app.df)
            self._tabla_completa = tabla

            self.card_min.actualizar("—" if minimo == -1 else str(minimo))
            self.card_max.actualizar("—" if maximo == -1 else str(maximo))
            self.card_prom.actualizar("—" if promedio == -1 else f"{promedio:.2f}")
            self.aplicar_filtro()
            self._set_status("Datos actualizados.")
        except Exception as exc:
            self._set_error(f"No se pudieron calcular las estadísticas de autoría: {exc}")
            self._set_status("")

    def aplicar_filtro(self) -> None:
        self.tree.delete(*self.tree.get_children())
        if self._tabla_completa is None:
            return
        consulta = self.busqueda_var.get().strip().lower()
        tabla = self._tabla_completa
        if consulta:
            tabla = tabla[tabla["Universidad_Institucion"].astype(str).str.lower().str.contains(consulta, na=False)]

        for _, fila in tabla.iterrows():
            self.tree.insert(
                "",
                "end",
                values=(
                    fila["Universidad_Institucion"],
                    fila["Total_Articulos"],
                    fila["Promedio_Autores"],
                    fila["Maximo_Autores"],
                    fila["Total_Individuales"],
                    fila["Total_Colaborativos"],
                ),
            )

    def on_show(self) -> None:
        if self.app.df is not None:
            self.cargar_datos()


class VistaTopAutores(_BaseVistaDatos):
    def __init__(self, parent: tk.Widget, app: tk.Misc):
        super().__init__(parent, app, "Top 10 autores")
        self.btn_actualizar.configure(command=self.cargar_datos)

        contenedor = tk.Frame(self, bg=BG)
        contenedor.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=24, pady=(0, 24))
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(contenedor, bg=BG, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(contenedor, orient="vertical", command=self.canvas.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=scroll.set)

        self.inner = tk.Frame(self.canvas, bg=BG)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_inner_configure(self, _event=None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event=None) -> None:
        self.canvas.itemconfigure(self.canvas_window, width=event.width if event else self.canvas.winfo_width())

    def cargar_datos(self) -> None:
        self._set_error("")
        self._limpiar_cards()
        if not self._verificar_df():
            return
        if "Author full names" not in self.app.df.columns:
            self._set_error("La columna 'Author full names' no está disponible en el archivo cargado.")
            return
        self._set_status("Calculando…")
        self.after(10, self._calcular)

    def _calcular(self) -> None:
        try:
            nombres = top_autores(self.app.df.copy(), "autores")
            publicaciones = top_autores(self.app.df.copy(), "num_publi")
            titulos = top_autores(self.app.df.copy(), "titulos")
            if nombres == -1 or not nombres:
                self._set_error("No hay suficientes datos para construir el top 10 de autores.")
                self._set_status("")
                return

            for idx, nombre in enumerate(nombres, start=1):
                cantidad = int(publicaciones.get(nombre, 0)) if hasattr(publicaciones, "get") else 0
                lista_titulos = list(titulos.get(nombre, [])) if hasattr(titulos, "get") else []
                self._agregar_card(idx, nombre, cantidad, lista_titulos)
            self._set_status("Datos actualizados.")
        except Exception as exc:
            self._set_error(f"No se pudo construir el top de autores: {exc}")
            self._set_status("")

    def _agregar_card(self, posicion: int, nombre: str, publicaciones: int, titulos: list[str]) -> None:
        card = tk.Frame(self.inner, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", pady=6)
        card.grid_columnconfigure(1, weight=1)

        tk.Label(card, text=f"{posicion:02}", bg="#ede9fe", fg=ACCENT, font=(FONT_FAMILY, 11, "bold"), width=4).grid(row=0, column=0, padx=12, pady=12)
        info = tk.Frame(card, bg=CARD)
        info.grid(row=0, column=1, sticky="ew", pady=12)
        info.grid_columnconfigure(0, weight=1)
        tk.Label(info, text=nombre, bg=CARD, fg=TEXT, font=(FONT_FAMILY, 11, "bold"), anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(info, text=f"{publicaciones} publicaciones", bg=CARD, fg=MUTED, font=(FONT_FAMILY, 10)).grid(row=1, column=0, sticky="w", pady=(4, 0))

        detalle = tk.Frame(card, bg="#fafafa")
        detalle.grid(row=1, column=0, columnspan=3, sticky="ew", padx=12, pady=(0, 12))
        detalle.grid_remove()
        for titulo in titulos:
            tk.Label(
                detalle,
                text=f"• {titulo}",
                bg="#fafafa",
                fg=TEXT,
                anchor="w",
                justify="left",
                wraplength=720,
                font=(FONT_FAMILY, 10),
            ).pack(fill="x", pady=2)

        boton = ColorButton(
            card,
            text="Mostrar títulos",
            bg="#f3f4f6",
            fg=TEXT,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
        )
        boton.configure(command=lambda d=detalle, b=boton: self._toggle_detalle(d, b))
        boton.grid(row=0, column=2, padx=12)

    def _toggle_detalle(self, detalle: tk.Frame, boton: tk.Button) -> None:
        if detalle.winfo_ismapped():
            detalle.grid_remove()
            boton.configure(text="Mostrar títulos")
        else:
            detalle.grid()
            boton.configure(text="Ocultar títulos")

    def _limpiar_cards(self) -> None:
        for widget in self.inner.winfo_children():
            widget.destroy()

    def on_show(self) -> None:
        if self.app.df is not None:
            self.cargar_datos()
