from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from gui_utils import (FONT_FAMILY, FONT_SM, FONT_MD, FONT_LG, PAD_HEADER, PAD_ENTRY,
                       ColorButton, styled_entry, styled_listbox, setup_treeview_tags, insert_striped)
from compat_imports import load_project_module

paises_mod = load_project_module("tops")
filtrado_mod = load_project_module("filtrado")
extraer_paises = paises_mod.extraer_paises
obtener_frecuencias_paises = paises_mod.obtener_frecuencias_paises
obtener_ranking_universidades = filtrado_mod.obtener_ranking_universidades
obtener_articulos_agrupados_por_universidad = filtrado_mod.obtener_articulos_agrupados_por_universidad
obtener_top_10_universidades_citadas = filtrado_mod.obtener_top_10_universidades_citadas
obtener_pais_universidades_top_10 = filtrado_mod.obtener_pais_universidades_top_10

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
        head.grid(row=0, column=0, sticky="ew", padx=24, pady=PAD_HEADER)
        head.grid_columnconfigure(0, weight=1)
        tk.Label(head, text=titulo, bg=BG, fg=TEXT, font=(FONT_FAMILY, FONT_LG, "bold")).grid(row=0, column=0, sticky="w")
        self.btn_actualizar = ColorButton(
            head,
            text="Actualizar",
            bg="#ede9fe",
            fg=ACCENT,
            relief="flat",
            activebackground="#ddd6fe",
            cursor="hand2",
            font=(FONT_FAMILY, FONT_MD, "bold"),
            padx=14,
            pady=8,
        )
        self.btn_actualizar.grid(row=0, column=1, sticky="e")
        self.status_label = tk.Label(head, text="", bg=BG, fg=MUTED, font=(FONT_FAMILY, FONT_MD))
        self.status_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))
        self.error_label = tk.Label(head, text="", bg=BG, fg=ERROR, font=(FONT_FAMILY, FONT_MD), wraplength=780, justify="left")
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
        self.lbl_total_paises = tk.Label(resumen, text="Países únicos: —", bg=BG, fg=TEXT, font=(FONT_FAMILY, FONT_MD, "bold"))
        self.lbl_total_paises.grid(row=0, column=0, sticky="w")
        self.lbl_total_articulos = tk.Label(resumen, text="Artículos con afiliación: —", bg=BG, fg=MUTED, font=(FONT_FAMILY, FONT_MD))
        self.lbl_total_articulos.grid(row=0, column=1, sticky="w", padx=(20, 0))

        filtro = tk.Frame(self, bg=BG)
        filtro.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 10))
        filtro.grid_columnconfigure(1, weight=1)
        tk.Label(filtro, text="Buscar país:", bg=BG, fg=TEXT, font=(FONT_FAMILY, FONT_MD, "bold")).grid(row=0, column=0, sticky="w")
        self.busqueda_var = tk.StringVar()
        self.busqueda_var.trace_add("write", lambda *_: self.aplicar_filtro())
        styled_entry(filtro, textvariable=self.busqueda_var, font=(FONT_FAMILY, FONT_MD)).grid(row=0, column=1, sticky="ew", padx=(10, 0), ipady=PAD_ENTRY)
        self._export_paises_sel = False
        self._export_top10_sel = False
        self._btn_exportar_paises = ColorButton(
            filtro, text="Exportar ▾", command=self._show_exportar_menu,
            bg="#f3f4f6", fg=TEXT, relief="flat", cursor="hand2", padx=12, pady=7)
        self._btn_exportar_paises.grid(row=0, column=2, padx=(8, 0))
        self.app.registrar_toggle_cb("paises", self._on_toggle_cb_paises)
        self.app.registrar_toggle_cb("paises_top10", self._on_toggle_cb_paises_top10)

        leyenda_frame = tk.Frame(self, bg=BG)
        leyenda_frame.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 4))
        tk.Frame(leyenda_frame, bg="#d9f99d", width=16, height=16).pack(side="left")
        tk.Label(leyenda_frame, text=" = Top 10 países con más artículos", bg=BG, fg=MUTED, font=(FONT_FAMILY, FONT_MD)).pack(side="left")

        tabla_card = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        tabla_card.grid(row=4, column=0, sticky="nsew", padx=24, pady=(0, 10))
        tabla_card.grid_rowconfigure(0, weight=1)
        tabla_card.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.tree = ttk.Treeview(tabla_card, columns=("Pais", "Articulos"), show="headings")
        self.tree.heading("Pais", text="País")
        self.tree.heading("Articulos", text="Artículos")
        self.tree.column("Pais", width=340, anchor="w")
        self.tree.column("Articulos", width=140, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._mostrar_porcentaje)
        setup_treeview_tags(self.tree)
        self.tree.tag_configure("top10", background="#d9f99d")
        scroll = ttk.Scrollbar(tabla_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

        self.porcentaje_label = tk.Label(self, text="", bg=BG, fg=MUTED, font=(FONT_FAMILY, FONT_MD))
        self.porcentaje_label.grid(row=5, column=0, sticky="w", padx=24, pady=(0, 24))

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
            self.app.export_getters["paises"] = lambda: self._tabla_completa
            self.app.export_getters["paises_top10"] = lambda: self._tabla_completa
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
        top10_paises = {fila[0] for fila in self._tabla_completa[:10]}
        for idx, (pais, conteo) in enumerate(datos):
            if pais in top10_paises:
                self.tree.insert("", "end", values=(pais, conteo), tags=("top10",))
            else:
                insert_striped(self.tree, idx, (pais, conteo))
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

    def _show_exportar_menu(self) -> None:
        if not self._tabla_completa:
            messagebox.showwarning("Sin datos", "Carga los datos primero.")
            return
        menu = tk.Menu(self, tearoff=0)
        lista_check = "✓  " if self._export_paises_sel else "     "
        top10_check = "✓  " if self._export_top10_sel else "     "
        menu.add_command(
            label=f"{lista_check}Lista completa",
            command=lambda: self.app.toggle_exportacion("paises"),
        )
        menu.add_command(
            label=f"{top10_check}Top 10 países",
            command=lambda: self.app.toggle_exportacion("paises_top10"),
        )
        btn = self._btn_exportar_paises
        menu.post(btn.winfo_rootx(), btn.winfo_rooty() + btn.winfo_height())

    def _update_exportar_btn(self) -> None:
        if self._export_paises_sel or self._export_top10_sel:
            self._btn_exportar_paises.configure(bg="#22c55e", fg="white", text="✓ Exportar ▾")
        else:
            self._btn_exportar_paises.configure(bg="#f3f4f6", fg=TEXT, text="Exportar ▾")

    def _on_toggle_cb_paises(self, seleccionado: bool) -> None:
        self._export_paises_sel = seleccionado
        self._update_exportar_btn()

    def _on_toggle_cb_paises_top10(self, seleccionado: bool) -> None:
        self._export_top10_sel = seleccionado
        self._update_exportar_btn()

    def on_show(self) -> None:
        if self.app.df is not None:
            self.cargar_datos()


class VistaUniversidades(_BaseVistaGeo):
    def __init__(self, parent: tk.Widget, app: tk.Misc):
        super().__init__(parent, app, "Universidades")
        self.btn_actualizar.configure(command=self.cargar_datos)
        self._articulos_por_universidad = {}
        self._ranking = None
        self._top = None
        self._pais_por_universidad = {}

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
        setup_treeview_tags(self.tree_general)
        scroll = ttk.Scrollbar(tabla_card, orient="vertical", command=self.tree_general.yview)
        self.tree_general.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

        acciones_gen = tk.Frame(self.tab_general, bg=BG)
        acciones_gen.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 8))
        self._btn_exportar_ranking = ColorButton(
            acciones_gen, text="Exportar ✓", command=self._toggle_exportar_ranking,
            bg="#f3f4f6", fg=TEXT, relief="flat", cursor="hand2", padx=12, pady=7)
        self._btn_exportar_ranking.pack(side="left")
        self.app.registrar_toggle_cb("univ_lista", self._on_toggle_cb_ranking)

        detalle_card = tk.Frame(self.tab_general, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        detalle_card.grid(row=0, column=1, sticky="nsew", pady=10)
        detalle_card.grid_rowconfigure(1, weight=1)
        detalle_card.grid_columnconfigure(0, weight=1)
        tk.Label(detalle_card, text="Artículos de la universidad seleccionada", bg=CARD, fg=TEXT, font=(FONT_FAMILY, FONT_MD + 2, "bold")).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 8))
        self.listbox_titulos = styled_listbox(detalle_card, font=(FONT_FAMILY, FONT_MD))
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
            tk.Label(filtros, text=titulo, bg=BG, fg=TEXT, font=(FONT_FAMILY, FONT_MD, "bold")).grid(row=0, column=idx * 2, sticky="w")
            styled_entry(filtros, textvariable=variable, font=(FONT_FAMILY, FONT_MD)).grid(row=0, column=idx * 2 + 1, sticky="ew", padx=(6, 12), ipady=PAD_ENTRY)

        botones = tk.Frame(self.tab_top, bg=BG)
        botones.grid(row=1, column=0, sticky="nw", pady=(0, 10))
        ColorButton(botones, text="Aplicar filtros", command=self.aplicar_filtros, bg=ACCENT, fg="white", relief="flat", cursor="hand2", padx=12, pady=7).pack(side="left")
        ColorButton(botones, text="Limpiar filtros", command=self.limpiar_filtros, bg="#f3f4f6", fg=TEXT, relief="flat", cursor="hand2", padx=12, pady=7).pack(side="left", padx=(8, 0))
        self._btn_exportar_top_univ = ColorButton(
            botones, text="Exportar ✓", command=self._toggle_exportar_top,
            bg="#f3f4f6", fg=TEXT, relief="flat", cursor="hand2", padx=12, pady=7)
        self._btn_exportar_top_univ.pack(side="left", padx=(8, 0))
        self.app.registrar_toggle_cb("univ_top", self._on_toggle_cb_top_univ)

        tabla_card = tk.Frame(self.tab_top, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        tabla_card.grid(row=2, column=0, sticky="nsew")
        tabla_card.grid_rowconfigure(0, weight=1)
        tabla_card.grid_columnconfigure(0, weight=1)

        self.tree_top = ttk.Treeview(tabla_card, columns=("Universidad_Institucion", "Numero_Articulos", "Citas_Totales", "Pais"), show="headings")
        self.tree_top.heading("Universidad_Institucion", text="Universidad")
        self.tree_top.heading("Numero_Articulos", text="Artículos")
        self.tree_top.heading("Citas_Totales", text="Citas totales")
        self.tree_top.heading("Pais", text="País")
        self.tree_top.column("Universidad_Institucion", width=270, anchor="w")
        self.tree_top.column("Numero_Articulos", width=100, anchor="center")
        self.tree_top.column("Citas_Totales", width=100, anchor="center")
        self.tree_top.column("Pais", width=150, anchor="w")
        self.tree_top.grid(row=0, column=0, sticky="nsew")
        setup_treeview_tags(self.tree_top)
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
            self._ranking = ranking
            pais_top = obtener_pais_universidades_top_10(self.app.df)
            self._pais_por_universidad = {
                str(fila["Universidad_Institucion"]): str(fila["Pais"])
                for _, fila in pais_top.iterrows()
            }
            agrupados = obtener_articulos_agrupados_por_universidad(self.app.df)
            self._articulos_por_universidad = {
                str(fila["Universidad_Institucion"]): list(fila["Lista_De_Titulos"])
                for _, fila in agrupados.iterrows()
            }
            self.app.export_getters["univ_lista"] = lambda: self._ranking
            self.tree_general.delete(*self.tree_general.get_children())
            for idx, (_, fila) in enumerate(ranking.iterrows()):
                insert_striped(self.tree_general, idx, (fila["Universidad_Institucion"], fila["Numero_Articulos"]))
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
            self._top = top
            self.app.export_getters["univ_top"] = lambda: self._top
            self.tree_top.delete(*self.tree_top.get_children())
            for idx, (_, fila) in enumerate(top.iterrows()):
                pais_val = self._pais_por_universidad.get(str(fila["Universidad_Institucion"]), "—")
                insert_striped(self.tree_top, idx, (fila["Universidad_Institucion"], fila["Numero_Articulos"], fila["Citas_Totales"], pais_val))
        except Exception as exc:
            self._set_error(f"No se pudieron aplicar los filtros: {exc}")

    def _toggle_exportar_ranking(self) -> None:
        if self._ranking is None:
            messagebox.showwarning("Sin datos", "Carga los datos primero.")
            return
        self.app.toggle_exportacion("univ_lista")

    def _on_toggle_cb_ranking(self, seleccionado: bool) -> None:
        if seleccionado:
            self._btn_exportar_ranking.configure(bg="#22c55e", fg="white", text="✓ Exportar")
        else:
            self._btn_exportar_ranking.configure(bg="#f3f4f6", fg=TEXT, text="Exportar ✓")

    def _toggle_exportar_top(self) -> None:
        if self._top is None:
            messagebox.showwarning("Sin datos", "Carga los datos primero.")
            return
        self.app.toggle_exportacion("univ_top")

    def _on_toggle_cb_top_univ(self, seleccionado: bool) -> None:
        if seleccionado:
            self._btn_exportar_top_univ.configure(bg="#22c55e", fg="white", text="✓ Exportar")
        else:
            self._btn_exportar_top_univ.configure(bg="#f3f4f6", fg=TEXT, text="Exportar ✓")

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
