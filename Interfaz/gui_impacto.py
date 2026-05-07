from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from gui_utils import FONT_FAMILY, ColorButton, styled_entry, bind_mousewheel, bind_mousewheel_recursive, setup_treeview_tags, insert_striped
from compat_imports import load_project_module

impacto_mod = load_project_module("impacto")
tops_mod = load_project_module("tops")
trabajos_mas_citados = impacto_mod.trabajos_mas_citados
calcular_promedio_citas_anual = impacto_mod.calcular_promedio_citas_anual
ordenar_por_promedio_citas = impacto_mod.ordenar_por_promedio_citas
top_10_trabajos = tops_mod.top_10_trabajos

BG = "#f5f5f5"
CARD = "#ffffff"
TEXT = "#1f2937"
MUTED = "#6b7280"
ACCENT = "#7c3aed"
BORDER = "#e5e7eb"
ERROR = "#991b1b"
LINK = "#2563eb"


class ScrollableCanvas(tk.Frame):
    def __init__(self, parent: tk.Widget, bg: str = BG):
        super().__init__(parent, bg=bg)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scroll.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        bind_mousewheel(self.canvas, self.canvas)
        bind_mousewheel(self.inner, self.canvas)

    def _on_inner_configure(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event=None):
        width = event.width if event else self.canvas.winfo_width()
        self.canvas.itemconfigure(self.window, width=width)

    def clear(self):
        for widget in self.inner.winfo_children():
            widget.destroy()
        self.canvas.yview_moveto(0)


class _BaseImpacto(tk.Frame):
    def __init__(self, parent: tk.Widget, app: tk.Misc, titulo: str):
        super().__init__(parent, bg=BG)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        head = tk.Frame(self, bg=BG)
        head.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 10))
        head.grid_columnconfigure(0, weight=1)
        tk.Label(head, text=titulo, bg=BG, fg=TEXT, font=(FONT_FAMILY, 20, "bold")).grid(row=0, column=0, sticky="w")
        self.btn_actualizar = ColorButton(head, text="Actualizar", bg="#ede9fe", fg=ACCENT, relief="flat", cursor="hand2", font=(FONT_FAMILY, 10, "bold"), padx=14, pady=8)
        self.btn_actualizar.grid(row=0, column=1, sticky="e")
        self.status_label = tk.Label(head, text="", bg=BG, fg=MUTED, font=(FONT_FAMILY, 10))
        self.status_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))
        self.error_label = tk.Label(head, text="", bg=BG, fg=ERROR, font=(FONT_FAMILY, 10), wraplength=780, justify="left")
        self.error_label.grid(row=2, column=0, columnspan=2, sticky="w")

    def _set_status(self, texto: str = ""):
        self.status_label.configure(text=texto)

    def _set_error(self, texto: str = ""):
        self.error_label.configure(text=texto)

    def _verificar_df(self) -> bool:
        if self.app.df is None or getattr(self.app.df, "empty", False):
            self._set_error("No hay un archivo cargado todavía.")
            return False
        return True

    def _run_in_thread(self, worker):
        threading.Thread(target=worker, daemon=True).start()


class VistaTrabajosCitados(_BaseImpacto):
    _BATCH = 100

    def __init__(self, parent: tk.Widget, app: tk.Misc):
        super().__init__(parent, app, "Trabajos más citados")
        self.btn_actualizar.configure(command=self.cargar_datos)
        self._datos = []
        self._datos_filtrados = []
        self._offset = 0
        self._cargando_mas = False
        self._carga_pendiente = False
        self._nota_widget = None
        self._tooltip_after = None

        filtro = tk.Frame(self, bg=BG)
        filtro.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 10))
        filtro.grid_columnconfigure(1, weight=1)
        tk.Label(filtro, text="Buscar referencia:", bg=BG, fg=TEXT, font=(FONT_FAMILY, 10, "bold")).grid(row=0, column=0, sticky="w")
        self.busqueda_var = tk.StringVar()
        self.busqueda_var.trace_add("write", lambda *_: self.aplicar_filtro())
        styled_entry(filtro, textvariable=self.busqueda_var, font=(FONT_FAMILY, 10)).grid(row=0, column=1, sticky="ew", padx=(10, 0), ipady=6)

        self.scrollable = ScrollableCanvas(self, bg=BG)
        self.scrollable.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 8))

        # Interceptar yscrollcommand para detectar cuando el usuario llega al fondo.
        # Se difiere _cargar_mas con after() para evitar re-entrancia dentro del callback.
        def _on_yview(first, last):
            self.scrollable.scroll.set(first, last)
            if float(last) >= 0.80 and not self._cargando_mas and not self._carga_pendiente:
                self._carga_pendiente = True
                self.after(10, self._trigger_carga)
        self.scrollable.canvas.configure(yscrollcommand=_on_yview)

        self.copy_label = tk.Label(self, text="", bg=BG, fg=ACCENT, font=(FONT_FAMILY, 10, "bold"))
        self.copy_label.grid(row=3, column=0, sticky="w", padx=24, pady=(0, 24))

    def cargar_datos(self) -> None:
        self._set_error("")
        self.scrollable.clear()
        if not self._verificar_df():
            return
        self._set_status("Calculando…")
        df_copy = self.app.df.copy()

        def worker():
            try:
                datos = trabajos_mas_citados(df_copy)
                self.after(0, lambda: self._carga_exitosa(datos))
            except Exception as exc:
                self.after(0, lambda: self._set_error(f"No se pudo calcular la lista de trabajos citados: {exc}"))
                self.after(0, lambda: self._set_status(""))

        self._run_in_thread(worker)

    def _carga_exitosa(self, datos):
        self._datos = list(datos)
        self.aplicar_filtro()
        self._set_status("Datos actualizados.")

    def aplicar_filtro(self) -> None:
        self.scrollable.clear()
        self._nota_widget = None
        self._offset = 0
        consulta = self.busqueda_var.get().strip().lower()
        if consulta:
            self._datos_filtrados = [item for item in self._datos if consulta in str(item[0]).lower()]
        else:
            self._datos_filtrados = self._datos
        self._renderizar_lote()

    def _renderizar_lote(self) -> None:
        lote = self._datos_filtrados[self._offset: self._offset + self._BATCH]
        for idx, (referencia, citas) in enumerate(lote, start=self._offset + 1):
            self._agregar_item(idx, referencia, citas)
        self._offset += len(lote)
        # Forzar recálculo de geometría antes de actualizar scrollregion
        self.scrollable.inner.update_idletasks()
        self.scrollable.canvas.configure(scrollregion=self.scrollable.canvas.bbox("all"))
        self._actualizar_nota()

    def _trigger_carga(self) -> None:
        """Punto de entrada diferido desde _on_yview (evita re-entrancia en yscrollcommand)."""
        self._carga_pendiente = False
        self._cargar_mas()

    def _cargar_mas(self) -> None:
        if self._cargando_mas or self._offset >= len(self._datos_filtrados):
            return
        self._cargando_mas = True
        try:
            if self._nota_widget is not None:
                try:
                    self._nota_widget.destroy()
                except tk.TclError:
                    pass
                self._nota_widget = None
            self._renderizar_lote()
        finally:
            self._cargando_mas = False

    def _actualizar_nota(self) -> None:
        if self._nota_widget is not None:
            try:
                self._nota_widget.destroy()
            except tk.TclError:
                pass
            self._nota_widget = None
        restantes = len(self._datos_filtrados) - self._offset
        if restantes <= 0:
            # Mostrar fin de lista cuando ya no hay más datos
            self._nota_widget = tk.Label(
                self.scrollable.inner,
                text=f"— Fin de la lista · {self._offset} trabajos citados en total —",
                bg=BG, fg=MUTED,
                font=(FONT_FAMILY, 10),
                anchor="center",
                pady=12,
            )
            self._nota_widget.pack(fill="x", pady=(4, 16))
            bind_mousewheel(self._nota_widget, self.scrollable.canvas)
            return
        texto = f"Cargar {min(restantes, self._BATCH)} más  ({self._offset} de {len(self._datos_filtrados)} mostrados)"
        self._nota_widget = ColorButton(
            self.scrollable.inner,
            text=texto,
            command=self._cargar_mas,
            bg="#ede9fe",
            fg=ACCENT,
            activebackground="#ddd6fe",
            font=(FONT_FAMILY, 10, "bold"),
            pady=10,
        )
        self._nota_widget.pack(fill="x", pady=(8, 4))
        bind_mousewheel_recursive(self._nota_widget, self.scrollable.canvas)

    def _agregar_item(self, indice: int, referencia: str, citas: int) -> None:
        card = tk.Frame(self.scrollable.inner, bg=CARD, highlightbackground=BORDER, highlightthickness=1, cursor="hand2")
        card.pack(fill="x", pady=6)
        titulo = tk.Label(card, text=f"{indice}. {citas} citas", bg=CARD, fg=TEXT, font=(FONT_FAMILY, 11, "bold"), anchor="w", cursor="hand2")
        titulo.pack(fill="x", padx=16, pady=(12, 4))
        detalle = tk.Label(card, text=referencia, bg=CARD, fg=TEXT, justify="left", wraplength=760, anchor="w", cursor="hand2", font=(FONT_FAMILY, 10))
        detalle.pack(fill="x", padx=16, pady=(0, 12))

        for widget in (card, titulo, detalle):
            widget.bind("<Button-1>", lambda _e, ref=referencia: self._copiar_referencia(ref))
        bind_mousewheel_recursive(card, self.scrollable.canvas)

    def _copiar_referencia(self, referencia: str) -> None:
        self.clipboard_clear()
        self.clipboard_append(referencia)
        self.copy_label.configure(text="¡Copiado!")
        if self._tooltip_after:
            self.after_cancel(self._tooltip_after)
        self._tooltip_after = self.after(1200, lambda: self.copy_label.configure(text=""))

    def on_show(self) -> None:
        if self.app.df is not None:
            self.cargar_datos()


class VistaPromedioCitas(_BaseImpacto):
    def __init__(self, parent: tk.Widget, app: tk.Misc):
        super().__init__(parent, app, "Promedio anual de citas")
        self.btn_actualizar.configure(command=self.cargar_datos)
        self._tabla = None
        self._sort = {"Title": False, "Year": False, "Promedio_Citas_Anual": False}

        filtro = tk.Frame(self, bg=BG)
        filtro.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 10))
        filtro.grid_columnconfigure(1, weight=1)
        tk.Label(filtro, text="Filtrar por título:", bg=BG, fg=TEXT, font=(FONT_FAMILY, 10, "bold")).grid(row=0, column=0, sticky="w")
        self.busqueda_var = tk.StringVar()
        self.busqueda_var.trace_add("write", lambda *_: self.aplicar_filtro())
        styled_entry(filtro, textvariable=self.busqueda_var, font=(FONT_FAMILY, 10)).grid(row=0, column=1, sticky="ew", padx=(10, 0), ipady=6)
        self._btn_exportar_citas = ColorButton(
            filtro, text="Exportar ✓", command=self._toggle_exportar_citas,
            bg="#f3f4f6", fg=TEXT, relief="flat", cursor="hand2", padx=12, pady=7)
        self._btn_exportar_citas.grid(row=0, column=2, padx=(8, 0))
        self.app.registrar_toggle_cb("citas", self._on_toggle_cb_citas)

        tabla_card = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        tabla_card.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 10))
        tabla_card.grid_rowconfigure(0, weight=1)
        tabla_card.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.tree = ttk.Treeview(tabla_card, columns=("Title", "Year", "Promedio_Citas_Anual"), show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")
        setup_treeview_tags(self.tree)
        headers = {
            "Title": "Título",
            "Year": "Año",
            "Promedio_Citas_Anual": "Promedio Citas/Año",
        }
        for col in headers:
            self.tree.heading(col, text=headers[col], command=lambda c=col: self.ordenar_por(c))
            self.tree.column(col, width=420 if col == "Title" else 130, anchor="w" if col == "Title" else "center")
        scroll = ttk.Scrollbar(tabla_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

        self.resumen = tk.Label(self, text="", bg=BG, fg=MUTED, justify="left", anchor="w", font=(FONT_FAMILY, 10))
        self.resumen.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 24))

    def cargar_datos(self) -> None:
        self._set_error("")
        self.tree.delete(*self.tree.get_children())
        if not self._verificar_df():
            return
        self._set_status("Calculando…")
        df_copy = self.app.df.copy()

        def worker():
            try:
                tabla = ordenar_por_promedio_citas(calcular_promedio_citas_anual(df_copy))
                self.after(0, lambda: self._carga_exitosa(tabla))
            except Exception as exc:
                self.after(0, lambda: self._set_error(f"No se pudo calcular el promedio anual de citas: {exc}"))
                self.after(0, lambda: self._set_status(""))

        self._run_in_thread(worker)

    def _carga_exitosa(self, tabla) -> None:
        self._tabla = tabla.copy()
        self.app.export_getters["citas"] = lambda: self._tabla
        self.aplicar_filtro()
        self._set_status("Datos actualizados.")

    def aplicar_filtro(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.resumen.configure(text="")
        if self._tabla is None:
            return
        tabla = self._tabla
        consulta = self.busqueda_var.get().strip().lower()
        if consulta:
            tabla = tabla[tabla["Title"].astype(str).str.lower().str.contains(consulta, na=False)]
        for idx, (_, fila) in enumerate(tabla.iterrows()):
            titulo = str(fila["Title"])
            if len(titulo) > 90:
                titulo = titulo[:87] + "…"
            insert_striped(self.tree, idx, (titulo, fila["Year"], fila["Promedio_Citas_Anual"]))
        self._actualizar_resumen(tabla)

    def ordenar_por(self, columna: str) -> None:
        if self._tabla is None:
            return
        asc = self._sort.get(columna, False)
        self._sort[columna] = not asc
        self._tabla = self._tabla.sort_values(by=columna, ascending=asc)
        self.aplicar_filtro()

    def _actualizar_resumen(self, tabla) -> None:
        if tabla is None or len(tabla) == 0:
            self.resumen.configure(text="")
            return
        promedio_general = float(tabla["Promedio_Citas_Anual"].mean())
        mayor = tabla.iloc[0]
        menor = tabla.iloc[-1]
        texto = (
            f"Promedio general: {promedio_general:.2f}\n"
            f"Mayor promedio: {str(mayor['Title'])[:70]} ({mayor['Promedio_Citas_Anual']})\n"
            f"Menor promedio: {str(menor['Title'])[:70]} ({menor['Promedio_Citas_Anual']})"
        )
        self.resumen.configure(text=texto)

    def _toggle_exportar_citas(self) -> None:
        if self._tabla is None:
            messagebox.showwarning("Sin datos", "Carga los datos primero.")
            return
        self.app.toggle_exportacion("citas")

    def _on_toggle_cb_citas(self, seleccionado: bool) -> None:
        if seleccionado:
            self._btn_exportar_citas.configure(bg="#22c55e", fg="white", text="✓ Exportar")
        else:
            self._btn_exportar_citas.configure(bg="#f3f4f6", fg=TEXT, text="Exportar ✓")

    def on_show(self) -> None:
        if self.app.df is not None:
            self.cargar_datos()


class VistaTop10Trabajos(_BaseImpacto):
    def __init__(self, parent: tk.Widget, app: tk.Misc):
        super().__init__(parent, app, "Top 10 trabajos")
        self.btn_actualizar.configure(command=self.cargar_datos)
        self._datos = []

        acciones = tk.Frame(self, bg=BG)
        acciones.grid(row=1, column=0, sticky="w", padx=24, pady=(0, 10))
        self._btn_exportar_top_trab = ColorButton(
            acciones, text="Exportar ✓", command=self._toggle_exportar_top_trab,
            bg="#f3f4f6", fg=TEXT, relief="flat", cursor="hand2", padx=12, pady=7)
        self._btn_exportar_top_trab.pack(side="left")
        self.app.registrar_toggle_cb("top_trabajos", self._on_toggle_cb_top_trab)

        self.scrollable = ScrollableCanvas(self, bg=BG)
        self.scrollable.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 24))

    def cargar_datos(self) -> None:
        self._set_error("")
        self.scrollable.clear()
        if not self._verificar_df():
            return
        self._set_status("Calculando…")
        df_copy = self.app.df.copy()

        def worker():
            try:
                datos = top_10_trabajos(df_copy)
                self.after(0, lambda: self._carga_exitosa(datos))
            except Exception as exc:
                self.after(0, lambda: self._set_error(f"No se pudo construir el top 10 de trabajos: {exc}"))
                self.after(0, lambda: self._set_status(""))

        self._run_in_thread(worker)

    def _carga_exitosa(self, datos) -> None:
        self._datos = list(datos)
        self.app.export_getters["top_trabajos"] = lambda: self._datos
        for idx, (referencia, citas, anio, doi) in enumerate(self._datos, start=1):
            self._agregar_card(idx, referencia, citas, anio, doi)
        self._set_status("Datos actualizados.")

    def _agregar_card(self, indice: int, referencia: str, citas: int, anio, doi: str) -> None:
        card = tk.Frame(self.scrollable.inner, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", pady=6)

        cabecera = tk.Frame(card, bg=CARD)
        cabecera.pack(fill="x", padx=16, pady=(12, 8))
        tk.Label(cabecera, text=f"#{indice}", bg="#ede9fe", fg=ACCENT, font=(FONT_FAMILY, 11, "bold"), width=4).pack(side="left")
        tk.Label(cabecera, text=f"{citas} citas", bg=CARD, fg=TEXT, font=(FONT_FAMILY, 11, "bold")).pack(side="left", padx=(10, 12))
        tk.Label(cabecera, text=f"Año: {anio}", bg=CARD, fg=MUTED, font=(FONT_FAMILY, 10, "bold")).pack(side="left")

        tk.Label(card, text=referencia, bg=CARD, fg=TEXT, justify="left", anchor="w", wraplength=760, font=(FONT_FAMILY, 10)).pack(fill="x", padx=16, pady=(0, 12))

        if doi and str(doi).strip().lower() != "sin doi":
            enlace = tk.Label(card, text=f"https://doi.org/{doi}", bg=CARD, fg=LINK, cursor="hand2", font=(FONT_FAMILY, 10, "underline"))
            enlace.pack(anchor="w", padx=16, pady=(0, 12))
            enlace.bind("<Button-1>", lambda _e, value=doi: webbrowser.open(f"https://doi.org/{value}"))
        else:
            tk.Label(card, text="Sin DOI", bg=CARD, fg="#9ca3af", font=(FONT_FAMILY, 10)).pack(anchor="w", padx=16, pady=(0, 12))
        bind_mousewheel_recursive(card, self.scrollable.canvas)

    def _toggle_exportar_top_trab(self) -> None:
        if not self._datos:
            messagebox.showwarning("Sin datos", "Carga los datos primero.")
            return
        self.app.toggle_exportacion("top_trabajos")

    def _on_toggle_cb_top_trab(self, seleccionado: bool) -> None:
        if seleccionado:
            self._btn_exportar_top_trab.configure(bg="#22c55e", fg="white", text="✓ Exportar")
        else:
            self._btn_exportar_top_trab.configure(bg="#f3f4f6", fg=TEXT, text="Exportar ✓")

    def on_show(self) -> None:
        if self.app.df is not None:
            self.cargar_datos()
