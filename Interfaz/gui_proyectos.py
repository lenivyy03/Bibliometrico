import tkinter as tk
from tkinter import ttk, messagebox
from compat_imports import load_project_module
from gui_utils import (FONT_FAMILY, FONT_SM, FONT_MD, FONT_LG, PAD_HEADER, PAD_ENTRY,
                       ColorButton, styled_entry, setup_treeview_tags, insert_striped)

proyectos_mod = load_project_module('proyectos')
guardar_proyecto = proyectos_mod.guardar_proyecto
abrir_proyecto = proyectos_mod.abrir_proyecto
listar_proyectos = proyectos_mod.listar_proyectos
eliminar_proyecto = proyectos_mod.eliminar_proyecto

BG = '#f5f5f5'
CARD = '#ffffff'
TEXT = '#1f2937'
MUTED = '#6b7280'
ACCENT = '#7c3aed'
BORDER = '#e5e7eb'
SUCCESS = '#166534'
ERROR = '#991b1b'


class VistaProyectos(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._crear_encabezado()      # row=0
        self._crear_seccion_nuevo()   # row=1
        self._crear_seccion_guardar() # row=2
        self._crear_seccion_listar()  # row=3

    # ── Encabezado ────────────────────────────────────────────────────────────

    def _crear_encabezado(self):
        head = tk.Frame(self, bg=BG)
        head.grid(row=0, column=0, sticky='ew', padx=24, pady=PAD_HEADER)
        tk.Label(
            head, text='Gestión de Proyectos',
            bg=BG, fg=TEXT, font=(FONT_FAMILY, FONT_LG, 'bold'),
        ).pack(anchor='w')
        tk.Label(
            head, text='Crea, guarda y abre tus proyectos de análisis.',
            bg=BG, fg=MUTED, font=(FONT_FAMILY, FONT_SM),
        ).pack(anchor='w', pady=(2, 0))

    # ── Sección "Nuevo" (estilo Google Docs) ─────────────────────────────────

    def _crear_seccion_nuevo(self):
        seccion = tk.Frame(self, bg=BG)
        seccion.grid(row=1, column=0, sticky='ew', padx=24, pady=(0, 10))

        tk.Label(
            seccion, text='NUEVO',
            bg=BG, fg=MUTED, font=(FONT_FAMILY, FONT_SM, 'bold'),
        ).pack(anchor='w', pady=(0, 8))

        cards_row = tk.Frame(seccion, bg=BG)
        cards_row.pack(anchor='w')

        # ── Card "En blanco" ──────────────────────────────────────────────────
        card = tk.Frame(
            cards_row, bg=CARD,
            highlightbackground=BORDER, highlightthickness=1,
            cursor='hand2', width=112, height=120,
        )
        card.pack(side='left')
        card.pack_propagate(False)
        self._card_nuevo = card

        # Ícono de página (frames, sin emojis)
        page_wrap = tk.Frame(card, bg=CARD)
        page_wrap.place(relx=0.5, y=16, anchor='n')
        page_icon = tk.Frame(
            page_wrap, bg='#f3f4f6',
            highlightbackground='#d1d5db', highlightthickness=1,
            width=36, height=44,
        )
        page_icon.pack()
        page_icon.pack_propagate(False)
        for pady_top in (8, 4, 4):
            tk.Frame(page_icon, bg='#d1d5db', height=2).pack(
                fill='x', padx=6, pady=(pady_top, 0)
            )

        tk.Label(
            card, text='En blanco',
            bg=CARD, fg=TEXT, font=(FONT_FAMILY, FONT_SM),
        ).place(relx=0.5, rely=1.0, y=-12, anchor='s')

        # Hover + click
        def _hover_in(_e):
            card.configure(highlightbackground=ACCENT, highlightthickness=2)

        def _hover_out(_e):
            card.configure(highlightbackground=BORDER, highlightthickness=1)

        def _click(_e):
            self._mostrar_input_nombre()

        self._bind_card(card, _hover_in, _hover_out, _click)

        # ── Input de nombre (aparece bajo los cards) ──────────────────────────
        self._input_frame = tk.Frame(seccion, bg=BG)
        # Se monta con pack cuando el usuario hace clic

        tk.Label(
            self._input_frame, text='Nombre del proyecto:',
            bg=BG, fg=TEXT, font=(FONT_FAMILY, FONT_MD),
        ).pack(side='left', padx=(0, 8))

        self._nombre_var_nuevo = tk.StringVar()
        self._entry_nuevo = styled_entry(
            self._input_frame,
            textvariable=self._nombre_var_nuevo,
            font=(FONT_FAMILY, FONT_MD),
            width=24,
        )
        self._entry_nuevo.pack(side='left', ipady=PAD_ENTRY)
        self._entry_nuevo.bind('<Return>', lambda _e: self._confirmar_nuevo_proyecto())

        self._btn_crear = ColorButton(
            self._input_frame, text='Crear  →',
            command=self._confirmar_nuevo_proyecto,
            bg=ACCENT, fg='white', activebackground='#6d28d9',
            relief='flat', cursor='hand2',
            font=(FONT_FAMILY, FONT_MD, 'bold'), padx=14, pady=5,
        )
        self._btn_crear.pack(side='left', padx=(8, 0))

        ColorButton(
            self._input_frame, text='Cancelar',
            command=self._ocultar_input_nombre,
            bg=BG, fg=MUTED, activebackground='#e5e7eb',
            relief='flat', cursor='hand2',
            font=(FONT_FAMILY, FONT_MD), padx=8, pady=5,
        ).pack(side='left', padx=(4, 0))

        self._lbl_error_nuevo = tk.Label(
            seccion, text='',
            bg=BG, fg='#ef4444', font=(FONT_FAMILY, FONT_SM),
        )
        self._lbl_error_nuevo.pack(anchor='w')

    def _bind_card(self, widget, on_enter, on_leave, on_click):
        """Propaga hover y click a todos los hijos del card."""
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
        widget.bind('<Button-1>', on_click)
        for child in widget.winfo_children():
            child.bind('<Enter>', on_enter)
            child.bind('<Leave>', on_leave)
            child.bind('<Button-1>', on_click)

    def _mostrar_input_nombre(self):
        self._nombre_var_nuevo.set('')
        self._lbl_error_nuevo.configure(text='')
        self._input_frame.pack(anchor='w', pady=(10, 0))
        self._entry_nuevo.focus_set()

    def _ocultar_input_nombre(self):
        self._input_frame.pack_forget()
        self._nombre_var_nuevo.set('')
        self._lbl_error_nuevo.configure(text='')

    def _confirmar_nuevo_proyecto(self):
        nombre = self._nombre_var_nuevo.get().strip()
        if not nombre:
            self._lbl_error_nuevo.configure(text='Ingresa un nombre para el proyecto.')
            return

        self._lbl_error_nuevo.configure(text='')
        self.app.proyecto_pendiente = nombre

        # Feedback visual breve antes de navegar
        self._btn_crear.configure(text='Abriendo...', state='disabled')
        self.after(170, self._navegar_a_carga)

    def _navegar_a_carga(self):
        self._ocultar_input_nombre()
        self._btn_crear.configure(text='Crear  →', state='normal')
        self.app.cambiar_vista('carga')

    # ── Sección "Guardar proyecto actual" ─────────────────────────────────────

    def _crear_seccion_guardar(self):
        card = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        card.grid(row=2, column=0, sticky='ew', padx=24, pady=(0, 12))
        tk.Label(
            card, text='Guardar proyecto actual',
            bg=CARD, fg=TEXT, font=(FONT_FAMILY, FONT_MD + 2, 'bold'),
        ).pack(anchor='w', padx=16, pady=(14, 8))

        fila = tk.Frame(card, bg=CARD)
        fila.pack(fill='x', padx=16, pady=(0, 14))
        tk.Label(fila, text='Nombre:', bg=CARD, fg=TEXT, font=(FONT_FAMILY, FONT_MD)).pack(side='left')

        self.nombre_var = tk.StringVar()
        styled_entry(
            fila, textvariable=self.nombre_var, font=(FONT_FAMILY, FONT_MD),
        ).pack(side='left', padx=10, ipady=PAD_ENTRY, fill='x', expand=True)

        ColorButton(
            fila, text='Guardar', command=self.ejecutar_guardar,
            bg=ACCENT, fg='white', activebackground='#6d28d9',
            relief='flat', cursor='hand2',
            font=(FONT_FAMILY, FONT_MD, 'bold'), padx=16, pady=4,
        ).pack(side='left')

        self.lbl_mensaje_guardar = tk.Label(
            card, text='', bg=CARD, fg=TEXT, font=(FONT_FAMILY, FONT_MD),
        )
        self.lbl_mensaje_guardar.pack(anchor='w', padx=16, pady=(0, 8))

    # ── Sección "Proyectos guardados" ─────────────────────────────────────────

    def _crear_seccion_listar(self):
        card = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        card.grid(row=3, column=0, sticky='nsew', padx=24, pady=(0, 24))
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        head = tk.Frame(card, bg=CARD)
        head.grid(row=0, column=0, columnspan=2, sticky='ew', padx=16, pady=14)
        tk.Label(
            head, text='Proyectos guardados',
            bg=CARD, fg=TEXT, font=(FONT_FAMILY, FONT_MD + 2, 'bold'),
        ).pack(side='left')
        ColorButton(
            head, text='Actualizar lista', command=self.cargar_lista,
            bg='#f3f4f6', fg=TEXT, activebackground='#e5e7eb',
            relief='flat', cursor='hand2',
            font=(FONT_FAMILY, FONT_MD), padx=12, pady=4,
        ).pack(side='right')

        self.tree = ttk.Treeview(card, columns=('Nombre', 'Fecha'), show='headings')
        self.tree.heading('Nombre', text='Nombre del proyecto')
        self.tree.heading('Fecha', text='Última modificación')
        self.tree.column('Nombre', width=300, anchor='w')
        self.tree.column('Fecha', width=160, anchor='center')
        self.tree.grid(row=1, column=0, sticky='nsew', padx=(16, 0), pady=(0, 16))
        setup_treeview_tags(self.tree)

        scroll = ttk.Scrollbar(card, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.grid(row=1, column=1, sticky='ns', pady=(0, 16), padx=(0, 16))

        pie = tk.Frame(card, bg=CARD)
        pie.grid(row=2, column=0, columnspan=2, sticky='ew', padx=16, pady=(0, 14))
        ColorButton(
            pie, text='Abrir proyecto seleccionado', command=self.ejecutar_abrir,
            bg=ACCENT, fg='white', activebackground='#6d28d9',
            relief='flat', cursor='hand2',
            font=(FONT_FAMILY, FONT_MD, 'bold'), padx=16, pady=6,
        ).pack(side='left')
        ColorButton(
            pie, text='Eliminar proyecto', command=self.ejecutar_eliminar,
            bg='#dc2626', fg='white', activebackground='#b91c1c',
            relief='flat', cursor='hand2',
            font=(FONT_FAMILY, FONT_MD, 'bold'), padx=16, pady=6,
        ).pack(side='left', padx=(10, 0))
        self.lbl_mensaje_abrir = tk.Label(
            pie, text='', bg=CARD, fg=TEXT, font=(FONT_FAMILY, FONT_MD),
        )
        self.lbl_mensaje_abrir.pack(side='left', padx=10)

    # ── Acciones ──────────────────────────────────────────────────────────────

    def ejecutar_guardar(self):
        if self.app.df is None or getattr(self.app.df, 'empty', False):
            self.lbl_mensaje_guardar.configure(text='Carga un CSV primero.', fg=ERROR)
            return
        nombre = self.nombre_var.get().strip()
        if not nombre:
            self.lbl_mensaje_guardar.configure(text='Ingresa un nombre.', fg=ERROR)
            return
        try:
            guardar_proyecto(self.app.df, nombre)
            self.lbl_mensaje_guardar.configure(
                text='Proyecto guardado exitosamente.', fg=SUCCESS,
            )
            self.nombre_var.set('')
            self.cargar_lista()
        except Exception as e:
            self.lbl_mensaje_guardar.configure(text=str(e), fg=ERROR)

    def ejecutar_eliminar(self):
        seleccion = self.tree.selection()
        if not seleccion:
            self.lbl_mensaje_abrir.configure(text='Selecciona un proyecto.', fg=ERROR)
            return
        nombre = self.tree.item(seleccion[0], 'values')[0]
        if not messagebox.askyesno(
            'Eliminar proyecto',
            f'¿Eliminar "{nombre}"? Esta acción no se puede deshacer.',
        ):
            return
        try:
            eliminar_proyecto(nombre)
            self.cargar_lista()
            self.lbl_mensaje_abrir.configure(text=f'"{nombre}" eliminado.', fg=SUCCESS)
        except Exception as e:
            self.lbl_mensaje_abrir.configure(text=str(e), fg=ERROR)

    def ejecutar_abrir(self):
        seleccion = self.tree.selection()
        if not seleccion:
            self.lbl_mensaje_abrir.configure(text='Selecciona un proyecto.', fg=ERROR)
            return
        nombre = self.tree.item(seleccion[0], 'values')[0]
        try:
            df_cargado = abrir_proyecto(nombre)
            self.app.df = df_cargado
            self.app.actualizar_estado(nombre, len(df_cargado))
            self.app.habilitar_navegacion()
            self.lbl_mensaje_abrir.configure(
                text='Proyecto cargado exitosamente.', fg=SUCCESS,
            )
        except Exception as e:
            self.lbl_mensaje_abrir.configure(text=str(e), fg=ERROR)

    def cargar_lista(self):
        self.tree.delete(*self.tree.get_children())
        for idx, (nombre, fecha) in enumerate(listar_proyectos()):
            insert_striped(self.tree, idx, (nombre, fecha))

    def on_show(self):
        self.cargar_lista()
        self.lbl_mensaje_guardar.configure(text='')
        self.lbl_mensaje_abrir.configure(text='')
        self._ocultar_input_nombre()
