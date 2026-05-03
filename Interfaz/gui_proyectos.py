import tkinter as tk
from tkinter import ttk
from compat_imports import load_project_module

proyectos_mod = load_project_module('proyectos')
guardar_proyecto = proyectos_mod.guardar_proyecto
abrir_proyecto = proyectos_mod.abrir_proyecto
listar_proyectos = proyectos_mod.listar_proyectos

BG = '#f5f5f5'
CARD = '#ffffff'
TEXT = '#1f2937'
ACCENT = '#7c3aed'
BORDER = '#e5e7eb'
SUCCESS = '#166534'
ERROR = '#991b1b'

class VistaProyectos(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.crear_encabezado()
        self.crear_seccion_guardar()
        self.crear_seccion_listar()

    def crear_encabezado(self):
        head = tk.Frame(self, bg=BG)
        head.grid(row=0, column=0, sticky='ew', padx=24, pady=(24, 10))
        tk.Label(head, text='Gestion de Proyectos', bg=BG, fg=TEXT, font=('Segoe UI', 20, 'bold')).pack(side='left')

    def crear_seccion_guardar(self):
        card = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        card.grid(row=1, column=0, sticky='ew', padx=24, pady=(0, 16))
        tk.Label(card, text='Guardar proyecto actual', bg=CARD, fg=TEXT, font=('Segoe UI', 12, 'bold')).pack(anchor='w', padx=16, pady=(16, 8))
        fila = tk.Frame(card, bg=CARD)
        fila.pack(fill='x', padx=16, pady=(0, 16))
        tk.Label(fila, text='Nombre del proyecto:', bg=CARD, fg=TEXT, font=('Segoe UI', 10)).pack(side='left')
        self.nombre_var = tk.StringVar()
        tk.Entry(fila, textvariable=self.nombre_var, relief='solid', bd=1).pack(side='left', padx=10, ipady=4, fill='x', expand=True)
        tk.Button(fila, text='Guardar', command=self.ejecutar_guardar, bg=ACCENT, fg='white', relief='flat', cursor='hand2', padx=16, pady=4).pack(side='left')
        self.lbl_mensaje_guardar = tk.Label(card, text='', bg=CARD, font=('Segoe UI', 10))
        self.lbl_mensaje_guardar.pack(anchor='w', padx=16, pady=(0, 10))

    def crear_seccion_listar(self):
        card = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        card.grid(row=2, column=0, sticky='nsew', padx=24, pady=(0, 24))
        self.grid_rowconfigure(2, weight=1)
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)
        head = tk.Frame(card, bg=CARD)
        head.grid(row=0, column=0, sticky='ew', padx=16, pady=16)
        tk.Label(head, text='Proyectos guardados', bg=CARD, fg=TEXT, font=('Segoe UI', 12, 'bold')).pack(side='left')
        tk.Button(head, text='Actualizar lista', command=self.cargar_lista, bg='#f3f4f6', fg=TEXT, relief='flat', cursor='hand2', padx=12, pady=4).pack(side='right')
        self.tree = ttk.Treeview(card, columns=('Nombre',), show='headings')
        self.tree.heading('Nombre', text='Nombre del proyecto')
        self.tree.column('Nombre', width=400, anchor='w')
        self.tree.grid(row=1, column=0, sticky='nsew', padx=16, pady=(0, 16))
        scroll = ttk.Scrollbar(card, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.grid(row=1, column=1, sticky='ns', pady=(0, 16), padx=(0, 16))
        pie = tk.Frame(card, bg=CARD)
        pie.grid(row=2, column=0, sticky='ew', padx=16, pady=(0, 16))
        tk.Button(pie, text='Abrir proyecto seleccionado', command=self.ejecutar_abrir, bg=ACCENT, fg='white', relief='flat', cursor='hand2', padx=16, pady=6).pack(side='left')
        self.lbl_mensaje_abrir = tk.Label(pie, text='', bg=CARD, font=('Segoe UI', 10))
        self.lbl_mensaje_abrir.pack(side='left', padx=10)

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
            self.lbl_mensaje_guardar.configure(text='Proyecto guardado exitosamente.', fg=SUCCESS)
            self.nombre_var.set('')
            self.cargar_lista()
        except Exception as e:
            self.lbl_mensaje_guardar.configure(text=str(e), fg=ERROR)

    def ejecutar_abrir(self):
        seleccion = self.tree.selection()
        if not seleccion:
            self.lbl_mensaje_abrir.configure(text='Selecciona un proyecto.', fg=ERROR)
            return
        item = self.tree.item(seleccion[0], 'values')
        nombre = item[0]
        try:
            df_cargado = abrir_proyecto(nombre)
            self.app.df = df_cargado
            self.app.actualizar_estado(nombre, len(df_cargado))
            self.app.habilitar_navegacion()
            self.lbl_mensaje_abrir.configure(text='Proyecto cargado exitosamente.', fg=SUCCESS)
        except Exception as e:
            self.lbl_mensaje_abrir.configure(text=str(e), fg=ERROR)

    def cargar_lista(self):
        self.tree.delete(*self.tree.get_children())
        proyectos = listar_proyectos()
        for p in proyectos:
            self.tree.insert('', 'end', values=(p,))

    def on_show(self):
        self.cargar_lista()
        self.lbl_mensaje_guardar.configure(text='')
        self.lbl_mensaje_abrir.configure(text='')