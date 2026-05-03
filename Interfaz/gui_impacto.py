from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk
import webbrowser

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
        tk.Label(head, text=titulo, bg=BG, fg=TEXT, font=("Segoe UI", 20, "bold")).grid(row=0, column=0, sticky="w")
        self.btn_actualizar = tk.Button(head, text="Actualizar", bg="#ede9fe", fg=ACCENT, relief="flat", cursor="hand2", font=("Segoe UI", 10, "bold"), padx=14, pady=8)
        self.btn_actualizar.grid(row=0, column=1, sticky="e")
        self.status_label = tk.Label(head, text="", bg=BG, fg=MUTED, font=("Segoe UI", 10))
        self.status_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))
        self.error_label = tk.Label(head, text="", bg=BG, fg=ERROR, font=("Segoe UI", 10), wraplength=780, justify="left")
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
    def __init__(self, parent: tk.Widget, app: tk.Misc):
        super().__init__(parent, app, "Trabajos más citados")
        self.btn_actualizar.configure(command=self.cargar_datos)
        self._datos = []
        self._tooltip_after = None

        filtro = tk.Frame(self, bg=BG)
        filtro.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 10))
        filtro.grid_columnconfigure(1, weight=1)
        tk.Label(filtro, text="Buscar referencia:", bg=BG, fg=TEXT, font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.busqueda_var = tk.StringVar()
        self.busqueda_var.trace_add("write", lambda *_: self.aplicar_filtro())
        tk.Entry(filtro, textvariable=self.busqueda_var, relief="solid", bd=1, highlightthickness=0).grid(row=0, column=1, sticky="ew", padx=(10, 0), ipady=6)

        self.scrollable = ScrollableCanvas(self, bg=BG)
        self.scrollable.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 8))

        self.copy_label = tk.Label(self, text="", bg=BG, fg=ACCENT, font=("Segoe UI", 10, "bold"))
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
        consulta = self.busqueda_var.get().strip().lower()
        datos = self._datos
        if consulta:
            datos = [item for item in datos if consulta in str(item[0]).lower()]
        for idx, (referencia, citas) in enumerate(datos, start=1):
            self._agregar_item(idx, referencia, citas)

    def _agregar_item(self, indice: int, referencia: str, citas: int) -> None:
        card = tk.Frame(self.scrollable.inner, bg=CARD, highlightbackground=BORDER, highlightthickness=1, cursor="hand2")
        card.pack(fill="x", pady=6)
        titulo = tk.Label(card, text=f"{indice}. {citas} citas", bg=CARD, fg=TEXT, font=("Segoe UI", 11, "bold"), anchor="w", cursor="hand2")
        titulo.pack(fill="x", padx=16, pady=(12, 4))
        detalle = tk.Label(card, text=referencia, bg=CARD, fg=TEXT, justify="left", wraplength=760, anchor="w", cursor="hand2", font=("Segoe UI", 10))
        detalle.pack(fill="x", padx=16, pady=(0, 12))

        for widget in (card, titulo, detalle):
            widget.bind("<Button-1>", lambda _e, ref=referencia: self._copiar_referencia(ref))

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
        tk.Label(filtro, text="Filtrar por título:", bg=BG, fg=TEXT, font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.busqueda_var = tk.StringVar()
        self.busqueda_var.trace_add("write", lambda *_: self.aplicar_filtro())
        tk.Entry(filtro, textvariable=self.busqueda_var, relief="solid", bd=1, highlightthickness=0).grid(row=0, column=1, sticky="ew", padx=(10, 0), ipady=6)

        tabla_card = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        tabla_card.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 10))
        tabla_card.grid_rowconfigure(0, weight=1)
        tabla_card.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.tree = ttk.Treeview(tabla_card, columns=("Title", "Year", "Promedio_Citas_Anual"), show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")
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

        self.resumen = tk.Label(self, text="", bg=BG, fg=MUTED, justify="left", anchor="w", font=("Segoe UI", 10))
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
        for _, fila in tabla.iterrows():
            titulo = str(fila["Title"])
            if len(titulo) > 90:
                titulo = titulo[:87] + "…"
            self.tree.insert("", "end", values=(titulo, fila["Year"], fila["Promedio_Citas_Anual"]))
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

    def on_show(self) -> None:
        if self.app.df is not None:
            self.cargar_datos()


class VistaTop10Trabajos(_BaseImpacto):
    def __init__(self, parent: tk.Widget, app: tk.Misc):
        super().__init__(parent, app, "Top 10 trabajos")
        self.btn_actualizar.configure(command=self.cargar_datos)

        acciones = tk.Frame(self, bg=BG)
        acciones.grid(row=1, column=0, sticky="w", padx=24, pady=(0, 10))
        tk.Button(acciones, text="Exportar a Word", command=lambda: print("pendiente"), bg="#f3f4f6", fg=TEXT, relief="flat", cursor="hand2", padx=12, pady=7).pack(side="left")
        tk.Button(acciones, text="Exportar a Excel", command=lambda: print("pendiente"), bg="#f3f4f6", fg=TEXT, relief="flat", cursor="hand2", padx=12, pady=7).pack(side="left", padx=(8, 0))

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
        for idx, (referencia, citas, anio, doi) in enumerate(datos, start=1):
            self._agregar_card(idx, referencia, citas, anio, doi)
        self._set_status("Datos actualizados.")

    def _agregar_card(self, indice: int, referencia: str, citas: int, anio, doi: str) -> None:
        card = tk.Frame(self.scrollable.inner, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", pady=6)

        cabecera = tk.Frame(card, bg=CARD)
        cabecera.pack(fill="x", padx=16, pady=(12, 8))
        tk.Label(cabecera, text=f"#{indice}", bg="#ede9fe", fg=ACCENT, font=("Segoe UI", 11, "bold"), width=4).pack(side="left")
        tk.Label(cabecera, text=f"{citas} citas", bg=CARD, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(side="left", padx=(10, 12))
        tk.Label(cabecera, text=f"Año: {anio}", bg=CARD, fg=MUTED, font=("Segoe UI", 10, "bold")).pack(side="left")

        tk.Label(card, text=referencia, bg=CARD, fg=TEXT, justify="left", anchor="w", wraplength=760, font=("Segoe UI", 10)).pack(fill="x", padx=16, pady=(0, 12))

        if doi and str(doi).strip().lower() != "sin doi":
            enlace = tk.Label(card, text=f"https://doi.org/{doi}", bg=CARD, fg=LINK, cursor="hand2", font=("Segoe UI", 10, "underline"))
            enlace.pack(anchor="w", padx=16, pady=(0, 12))
            enlace.bind("<Button-1>", lambda _e, value=doi: webbrowser.open(f"https://doi.org/{value}"))
        else:
            tk.Label(card, text="Sin DOI", bg=CARD, fg="#9ca3af", font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(0, 12))

    def on_show(self) -> None:
        if self.app.df is not None:
            self.cargar_datos()
