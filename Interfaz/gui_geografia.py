from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from gui_utils import FONT_FAMILY, ColorButton
from compat_imports import load_project_module

paises_mod = load_project_module("lista_paises")
filtrado_mod = load_project_module("filtrado")

extraer_paises = paises_mod.extraer_paises
obtener_frecuencias_paises = paises_mod.obtener_frecuencias_paises
obtener_ranking_universidades = filtrado_mod.obtener_ranking_universidades
obtener_articulos_agrupados_por_universidad = filtrado_mod.obtener_articulos_agrupados_por_universidad
obtener_top_10_universidades_citadas = filtrado_mod.obtener_top_10_universidades_citadas

BG = "#f5f5f5"
CARD = "#ffffff"
TEXT = "#1f2937"
MUTED = "#6b7280"
ACCENT = "#7c3aed"
BORDER = "#e5e7eb"
ERROR = "#991b1b"


class _BaseVistaGeo(tk.Frame):
    def __init__(self, parent: tk.Widget, app: tk.Misc, titulo: str):
        super().__init__(parent, bg=BG)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

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


class VistaPaises(_BaseVistaGeo):
    def __init__(self, parent: tk.Widget, app: tk.Misc):
        super().__init__(parent, app, "Lista de países")
        self.btn_actualizar.configure(command=self.cargar_datos)
        self._tabla_completa = []

        resumen = tk.Frame(self, bg=BG)
        resumen.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 10))
        resumen.grid_columnconfigure(1, weight=1)
        self.lbl_total_paises = tk.Label(resumen, text="Países únicos: —", bg=BG, fg=TEXT, font=(FONT_FAMILY, 10, "bold"))
        self.lbl_total_paises.grid(row=0, column=0, sticky="w")
        self.lbl_total_articulos = tk.Label(resumen, text="Artículos con afiliación: —", bg=BG, fg=MUTED, font=(FONT_FAMILY, 10))
        self.lbl_total_articulos.grid(row=0, column=1, sticky="w", padx=(20, 0))

        filtro = tk.Frame(self, bg=BG)
        filtro.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 10))
        filtro.grid_columnconfigure(1, weight=1)
        tk.Label(filtro, text="Buscar país:", bg=BG, fg=TEXT, font=(FONT_FAMILY, 10, "bold")).grid(row=0, column=0, sticky="w")
        self.busqueda_var = tk.StringVar()
        self.busqueda_var.trace_add("write", lambda *_: self.aplicar_filtro())
        tk.Entry(filtro, textvariable=self.busqueda_var, relief="solid", bd=1, highlightthickness=0).grid(row=0, column=1, sticky="ew", padx=(10, 0), ipady=6)

        tabla_card = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        tabla_card.grid(row=3, column=0, sticky="nsew", padx=24, pady=(0, 10))
        tabla_card.grid_rowconfigure(0, weight=1)
        tabla_card.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.tree = ttk.Treeview(tabla_card, columns=("Pais", "Articulos"), show="headings")
        self.tree.heading("Pais", text="País")
        self.tree.heading("Articulos", text="Artículos")
        self.tree.column("Pais", width=340, anchor="w")
        self.tree.column("Articulos", width=140, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._mostrar_porcentaje)
        scroll = ttk.Scrollbar(tabla_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

        self.porcentaje_label = tk.Label(self, text="", bg=BG, fg=MUTED, font=(FONT_FAMILY, 10))
        self.porcentaje_label.grid(row=4, column=0, sticky="w", padx=24, pady=(0, 24))

    def cargar_datos(self) -> None:
        self._set_error("")
        if not self._verificar_df():
            return
        self._set_status("Calculando…")
        self.after(10, self._calcular)

    def _calcular(self) -> None:
        try:
            paises = extraer_paises(self.app.df)
            freqs = obtener_frecuencias_paises(paises)
            self._tabla_completa = [(pais, int(conteo)) for pais, conteo in freqs.items()]
            self.lbl_total_paises.configure(text=f"Países únicos: {len(freqs)}")
            total_articulos = int(self.app.df["Affiliations"].dropna().shape[0]) if "Affiliations" in self.app.df.columns else 0
            self.lbl_total_articulos.configure(text=f"Artículos con afiliación: {total_articulos}")
            self.aplicar_filtro()
            self._set_status("Datos actualizados.")
        except Exception as exc:
            self._set_error(f"No se pudo generar la lista de países: {exc}")
            self._set_status("")

    def aplicar_filtro(self) -> None:
        self.tree.delete(*self.tree.get_children())
        consulta = self.busqueda_var.get().strip().lower()
        datos = self._tabla_completa
        if consulta:
            datos = [fila for fila in datos if consulta in str(fila[0]).lower()]
        for pais, conteo in datos:
            self.tree.insert("", "end", values=(pais, conteo))
        self.porcentaje_label.configure(text="")

    def _mostrar_porcentaje(self, _event=None) -> None:
        seleccion = self.tree.selection()
        if not seleccion:
            return
        item = self.tree.item(seleccion[0], "values")
        if not item:
            return
        pais, conteo = item[0], int(item[1])
        total = sum(x[1] for x in self._tabla_completa) or 1
        porcentaje = (conteo / total) * 100
        self.porcentaje_label.configure(text=f"{pais} representa {porcentaje:.2f}% del total de afiliaciones contabilizadas.")

    def on_show(self) -> None:
        if self.app.df is not None:
            self.cargar_datos()


class VistaUniversidades(_BaseVistaGeo):
    def __init__(self, parent: tk.Widget, app: tk.Misc):
        super().__init__(parent, app, "Universidades")
        self.btn_actualizar.configure(command=self.cargar_datos)
        self._articulos_por_universidad = {}

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 24))
        self.grid_rowconfigure(2, weight=1)

        self.tab_general = tk.Frame(self.notebook, bg=BG)
        self.tab_top = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(self.tab_general, text="Ranking general")
        self.notebook.add(self.tab_top, text="Top 10 filtrado")

        self._crear_tab_general()
        self._crear_tab_top()

    def _crear_tab_general(self) -> None:
        self.tab_general.grid_rowconfigure(0, weight=1)
        self.tab_general.grid_columnconfigure(0, weight=2)
        self.tab_general.grid_columnconfigure(1, weight=3)

        tabla_card = tk.Frame(self.tab_general, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        tabla_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        tabla_card.grid_rowconfigure(0, weight=1)
        tabla_card.grid_columnconfigure(0, weight=1)

        self.tree_general = ttk.Treeview(tabla_card, columns=("Universidad_Institucion", "Numero_Articulos"), show="headings")
        self.tree_general.heading("Universidad_Institucion", text="Universidad")
        self.tree_general.heading("Numero_Articulos", text="Artículos")
        self.tree_general.column("Universidad_Institucion", width=320, anchor="w")
        self.tree_general.column("Numero_Articulos", width=120, anchor="center")
        self.tree_general.grid(row=0, column=0, sticky="nsew")
        self.tree_general.bind("<<TreeviewSelect>>", self._mostrar_articulos_universidad)
        scroll = ttk.Scrollbar(tabla_card, orient="vertical", command=self.tree_general.yview)
        self.tree_general.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

        detalle_card = tk.Frame(self.tab_general, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        detalle_card.grid(row=0, column=1, sticky="nsew", pady=10)
        detalle_card.grid_rowconfigure(1, weight=1)
        detalle_card.grid_columnconfigure(0, weight=1)
        tk.Label(detalle_card, text="Artículos de la universidad seleccionada", bg=CARD, fg=TEXT, font=(FONT_FAMILY, 12, "bold")).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 8))
        self.listbox_titulos = tk.Listbox(detalle_card, activestyle="none", borderwidth=0, highlightthickness=0, font=(FONT_FAMILY, 10))
        self.listbox_titulos.grid(row=1, column=0, sticky="nsew", padx=(16, 0), pady=(0, 16))
        scroll_list = ttk.Scrollbar(detalle_card, orient="vertical", command=self.listbox_titulos.yview)
        self.listbox_titulos.configure(yscrollcommand=scroll_list.set)
        scroll_list.grid(row=1, column=1, sticky="ns", padx=(0, 16), pady=(0, 16))

    def _crear_tab_top(self) -> None:
        self.tab_top.grid_rowconfigure(1, weight=1)
        self.tab_top.grid_columnconfigure(0, weight=1)

        filtros = tk.Frame(self.tab_top, bg=BG)
        filtros.grid(row=0, column=0, sticky="ew", pady=10)
        for i in range(10):
            filtros.grid_columnconfigure(i, weight=1)

        self.var_pais = tk.StringVar()
        self.var_desde = tk.StringVar()
        self.var_hasta = tk.StringVar()
        self.var_citas_min = tk.StringVar()
        self.var_citas_max = tk.StringVar()

        campos = [
            ("País", self.var_pais),
            ("Desde", self.var_desde),
            ("Hasta", self.var_hasta),
            ("Citas mín.", self.var_citas_min),
            ("Citas máx.", self.var_citas_max),
        ]
        for idx, (titulo, variable) in enumerate(campos):
            tk.Label(filtros, text=titulo, bg=BG, fg=TEXT, font=(FONT_FAMILY, 10, "bold")).grid(row=0, column=idx * 2, sticky="w")
            tk.Entry(filtros, textvariable=variable, relief="solid", bd=1, highlightthickness=0).grid(row=0, column=idx * 2 + 1, sticky="ew", padx=(6, 12), ipady=5)

        botones = tk.Frame(self.tab_top, bg=BG)
        botones.grid(row=1, column=0, sticky="nw", pady=(0, 10))
        ColorButton(botones, text="Aplicar filtros", command=self.aplicar_filtros, bg=ACCENT, fg="white", relief="flat", cursor="hand2", padx=12, pady=7).pack(side="left")
        ColorButton(botones, text="Limpiar filtros", command=self.limpiar_filtros, bg="#f3f4f6", fg=TEXT, relief="flat", cursor="hand2", padx=12, pady=7).pack(side="left", padx=(8, 0))

        tabla_card = tk.Frame(self.tab_top, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        tabla_card.grid(row=2, column=0, sticky="nsew")
        tabla_card.grid_rowconfigure(0, weight=1)
        tabla_card.grid_columnconfigure(0, weight=1)

        self.tree_top = ttk.Treeview(tabla_card, columns=("Universidad_Institucion", "Numero_Articulos", "Citas_Totales"), show="headings")
        self.tree_top.heading("Universidad_Institucion", text="Universidad")
        self.tree_top.heading("Numero_Articulos", text="Artículos")
        self.tree_top.heading("Citas_Totales", text="Citas totales")
        self.tree_top.column("Universidad_Institucion", width=360, anchor="w")
        self.tree_top.column("Numero_Articulos", width=120, anchor="center")
        self.tree_top.column("Citas_Totales", width=120, anchor="center")
        self.tree_top.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(tabla_card, orient="vertical", command=self.tree_top.yview)
        self.tree_top.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

    def cargar_datos(self) -> None:
        self._set_error("")
        if not self._verificar_df():
            return
        self._set_status("Calculando…")
        self.after(10, self._calcular_general)

    def _calcular_general(self) -> None:
        try:
            ranking = obtener_ranking_universidades(self.app.df)
            agrupados = obtener_articulos_agrupados_por_universidad(self.app.df)
            self._articulos_por_universidad = {
                str(fila["Universidad_Institucion"]): list(fila["Lista_De_Titulos"])
                for _, fila in agrupados.iterrows()
            }
            self.tree_general.delete(*self.tree_general.get_children())
            for _, fila in ranking.iterrows():
                self.tree_general.insert("", "end", values=(fila["Universidad_Institucion"], fila["Numero_Articulos"]))
            self._set_status("Datos actualizados.")
            self.aplicar_filtros()
        except Exception as exc:
            self._set_error(f"No se pudieron calcular las universidades: {exc}")
            self._set_status("")

    def _mostrar_articulos_universidad(self, _event=None) -> None:
        self.listbox_titulos.delete(0, "end")
        seleccion = self.tree_general.selection()
        if not seleccion:
            return
        valores = self.tree_general.item(seleccion[0], "values")
        if not valores:
            return
        universidad = valores[0]
        for titulo in self._articulos_por_universidad.get(universidad, []):
            self.listbox_titulos.insert("end", titulo)

    def aplicar_filtros(self) -> None:
        if self.app.df is None:
            return
        try:
            pais = self.var_pais.get().strip() or None
            year_inicio = self._int_or_none(self.var_desde.get())
            year_fin = self._int_or_none(self.var_hasta.get())
            citas_min = self._int_or_none(self.var_citas_min.get())
            citas_max = self._int_or_none(self.var_citas_max.get())

            top = obtener_top_10_universidades_citadas(
                self.app.df,
                pais_buscado=pais,
                year_inicio=year_inicio,
                year_fin=year_fin,
                citas_totales_minimas=citas_min,
                citas_totales_maximas=citas_max,
            )
            self.tree_top.delete(*self.tree_top.get_children())
            for _, fila in top.iterrows():
                self.tree_top.insert("", "end", values=(fila["Universidad_Institucion"], fila["Numero_Articulos"], fila["Citas_Totales"]))
        except Exception as exc:
            self._set_error(f"No se pudieron aplicar los filtros: {exc}")

    def limpiar_filtros(self) -> None:
        for variable in (self.var_pais, self.var_desde, self.var_hasta, self.var_citas_min, self.var_citas_max):
            variable.set("")
        self.aplicar_filtros()

    @staticmethod
    def _int_or_none(valor: str):
        valor = valor.strip()
        if not valor:
            return None
        return int(valor)

    def on_show(self) -> None:
        if self.app.df is not None:
            self.cargar_datos()
