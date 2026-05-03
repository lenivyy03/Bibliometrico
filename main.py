import os
import textwrap

# ─── Imports de los módulos del proyecto ──────────────────────────────────────
from carga import cargar_csv
from conteo import metricas_prod
from estadisticas_autoria import num_minimo_autores, num_maximo_autores, num_promedio_autores
from filtrado import (
    tabla_comparativa_autoria,
    obtener_ranking_universidades,
    obtener_articulos_agrupados_por_universidad,
    filtrar_universidades_por_pais,
    obtener_top_10_universidades_citadas,
)
from impacto import (
    trabajos_mas_citados,
    calcular_promedio_citas_anual,
    ordenar_por_promedio_citas,
)
from lista_paises import extraer_paises, obtener_frecuencias_paises
from tops import top_10_trabajos, top_autores

# ─── Estado global ────────────────────────────────────────────────────────────
df = None
nombre_archivo = None


# ══════════════════════════════════════════════════════════════════════════════
# UTILIDADES DE CONSOLA
# ══════════════════════════════════════════════════════════════════════════════

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')


def pausar():
    input("\n  Presiona Enter para continuar...")


def encabezado():
    limpiar_pantalla()
    estado = f"{nombre_archivo}  ({len(df)} registros)" if df is not None else "Sin archivo cargado"
    print("=" * 64)
    print("   BIBLIOMÉTRICO  —  Análisis de Literatura Científica")
    print(f"   Archivo: {estado}")
    print("=" * 64)


def mostrar_tabla(filas, encabezados, anchos):
    """Imprime una tabla sencilla con anchos de columna fijos."""
    if not filas:
        print("\n  (Sin datos para mostrar)")
        return

    fmt = "  " + "  ".join(f"{{:<{a}}}" for a in anchos)
    sep = "  " + "  ".join("─" * a for a in anchos)

    # Encabezados
    print(fmt.format(*[str(h)[:anchos[i]] for i, h in enumerate(encabezados)]))
    print(sep)

    # Filas
    for fila in filas:
        celdas = [str(v)[:anchos[i]] if len(str(v)) > anchos[i] else str(v)
                  for i, v in enumerate(fila)]
        print(fmt.format(*celdas))


def requiere_archivo():
    """Devuelve True si hay un DataFrame cargado, False si no (con mensaje)."""
    if df is None:
        print("\n  ✗  Primero debes cargar un archivo CSV.")
        pausar()
        return False
    return True


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1: CARGA DE DATOS  (HU 1–5)
# ══════════════════════════════════════════════════════════════════════════════

def flujo_carga():
    global df, nombre_archivo
    encabezado()
    print("\n  ── CARGA DE ARCHIVO CSV ──\n")
    ruta = input("  Ingresa la ruta del archivo CSV: ").strip()

    resultado = cargar_csv(ruta)

    # HU 3: aviso de error de formato
    if not resultado.get("ok"):
        error = resultado.get("error") or resultado.get("mensaje", "Error desconocido")
        print(f"\n  ✗  {error}")
        if resultado.get("faltantes_criticas"):
            falt = ", ".join(resultado["faltantes_criticas"])
            print(f"  Columnas críticas faltantes: {falt}")
        pausar()
        return

    df = resultado["dataframe"]
    nombre_archivo = os.path.basename(ruta)

    # HU 2: confirmación del número de registros
    print(f"\n  ✓  {resultado['mensaje']}")
    print(f"  Total de registros cargados: {resultado['total_registros']}")

    # HU 4: previsualización de las primeras filas
    print("\n  ── Vista previa (primeras 3 filas) ──")
    for i, fila in enumerate(resultado["preview"][:3], 1):
        print(f"\n  Registro {i}:")
        for clave, valor in list(fila.items())[:6]:
            print(f"    {str(clave):<18} {str(valor)[:50]}")

    # HU 5: advertencia de columnas faltantes y métricas afectadas
    if resultado.get("faltantes_apa"):
        falt = ", ".join(resultado["faltantes_apa"])
        print(f"\n  ⚠  Columnas APA faltantes: {falt}")

    if resultado.get("metricas_incompletas"):
        print("\n  ⚠  Métricas que quedarán incompletas:")
        for col, metricas in resultado["metricas_incompletas"].items():
            lista = ", ".join(metricas)
            print(f"     [{col}] → {lista}")

    pausar()


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2: PRODUCTIVIDAD  (HU 6–9)
# ══════════════════════════════════════════════════════════════════════════════

def flujo_productividad():
    if not requiere_archivo():
        return
    encabezado()
    print("\n  ── MÉTRICAS DE PRODUCTIVIDAD  (HU 6–9) ──\n")
    metricas = metricas_prod(df)
    if not metricas:
        pausar()
        return
    for clave, valor in metricas.items():
        print(f"  {clave:<35} {valor}")
    pausar()


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3: ESTADÍSTICAS DE AUTORÍA  (HU 11–14)
# ══════════════════════════════════════════════════════════════════════════════

def flujo_autoria():
    if not requiere_archivo():
        return
    while True:
        encabezado()
        print("\n  ── ESTADÍSTICAS DE AUTORÍA ──\n")
        print("  [1]  Mínimo de autores por artículo           (HU 11)")
        print("  [2]  Máximo de autores por artículo           (HU 12)")
        print("  [3]  Promedio de autores por artículo         (HU 13)")
        print("  [4]  Tabla comparativa por institución        (HU 14)")
        print("  [0]  Volver al menú principal")

        op = input("\n  Opción: ").strip()

        if op == '':
            continue
        elif op == '0':
            break

        elif op == '1':
            minimo = num_minimo_autores(df)
            if minimo == -1:
                print("\n  ✗  No se pudo calcular (columna 'Authors' no disponible).")
            else:
                print(f"\n  Mínimo de autores en un artículo: {minimo}")

        elif op == '2':
            maximo = num_maximo_autores(df)
            if maximo == -1:
                print("\n  ✗  No se pudo calcular (columna 'Authors' no disponible).")
            else:
                print(f"\n  Máximo de autores en un artículo: {maximo}")

        elif op == '3':
            promedio = num_promedio_autores(df)
            if promedio == -1:
                print("\n  ✗  No se pudo calcular (columna 'Authors' no disponible).")
            else:
                print(f"\n  Promedio de autores por artículo: {promedio:.2f}")

        elif op == '4':
            print("\n  Calculando, espera un momento...")
            tabla = tabla_comparativa_autoria(df)
            if tabla.empty:
                print("\n  (Sin datos de afiliación disponibles)")
            else:
                print(f"\n  (Mostrando las primeras 10 de {len(tabla)} instituciones)\n")
                encabezados_display = [
                    "Institución", "Artículos", "Prom.Aut.", "Máx.Aut.", "Individuales", "Colaborat."
                ]
                mostrar_tabla(
                    tabla.head(10).values.tolist(),
                    encabezados_display,
                    anchos=[38, 9, 9, 9, 12, 11]
                )
        else:
            print("\n  Opción inválida.")

        pausar()


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4: LISTA DE PAÍSES  (HU 20–22)
# ══════════════════════════════════════════════════════════════════════════════

def flujo_paises():
    if not requiere_archivo():
        return
    encabezado()
    print("\n  ── LISTA DE PAÍSES  (HU 20–22) ──\n")

    if 'Affiliations' not in df.columns:
        print("  ✗  La columna 'Affiliations' no está disponible.")
        pausar()
        return

    paises = extraer_paises(df)
    frecuencias = obtener_frecuencias_paises(paises)  # Ya ordenado de mayor a menor (HU 22)

    print(f"  Total de países únicos: {len(frecuencias)}\n")
    filas = [(pais, conteo) for pais, conteo in frecuencias.items()]
    mostrar_tabla(filas[:25], ["País", "Artículos"], anchos=[38, 10])

    if len(filas) > 25:
        print(f"\n  (Mostrando 25 de {len(filas)} países)")
    pausar()


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 5: TRABAJOS MÁS CITADOS  (HU 24)
# ══════════════════════════════════════════════════════════════════════════════

def flujo_trabajos_citados():
    if not requiere_archivo():
        return
    encabezado()
    print("\n  ── TRABAJOS MÁS CITADOS EN FORMATO APA  (HU 24) ──")
    print("\n  (Mostrando los 10 más citados)\n")

    lista = trabajos_mas_citados(df)
    if not lista:
        print("  (Sin datos)")
        pausar()
        return

    for i, (ref, citas) in enumerate(lista[:10], 1):
        print(f"  {i}.  [{citas} citas]")
        for linea in textwrap.wrap(ref, width=68):
            print(f"      {linea}")
        print()
    pausar()


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 6: PROMEDIO DE CITAS ANUAL  (HU 29–31)
# ══════════════════════════════════════════════════════════════════════════════

def flujo_promedio_citas():
    if not requiere_archivo():
        return
    encabezado()
    print("\n  ── PROMEDIO DE CITAS ANUAL  (HU 29–31) ──\n")

    if 'Year' not in df.columns or 'Cited by' not in df.columns:
        print("  ✗  Faltan columnas 'Year' o 'Cited by'.")
        pausar()
        return

    # Usamos una copia para no modificar el df global
    df_calc = calcular_promedio_citas_anual(df.copy())
    df_ordenado = ordenar_por_promedio_citas(df_calc)

    total = len(df_ordenado)
    print(f"  (Mostrando los primeros 15 de {total} artículos)\n")

    filas = [
        (textwrap.shorten(str(r[0]), width=42, placeholder="…"), int(r[1]), r[2])
        for r in df_ordenado.head(15).values.tolist()
    ]
    mostrar_tabla(filas, ["Título", "Año", "Prom. Citas/Año"], anchos=[44, 6, 15])
    pausar()


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 7: TOP 10 AUTORES  (HU 33–35)
# ══════════════════════════════════════════════════════════════════════════════

def flujo_top_autores():
    if not requiere_archivo():
        return
    encabezado()
    print("\n  ── TOP 10 AUTORES MÁS PRODUCTIVOS  (HU 33–35) ──\n")

    if 'Author full names' not in df.columns:
        print("  ✗  La columna 'Author full names' no está disponible.")
        pausar()
        return

    copia = df.copy()
    nombres   = top_autores(copia, 'autores')
    publis    = top_autores(copia, 'num_publi')
    titulos_s = top_autores(copia, 'titulos')

    if nombres == -1 or not nombres:
        print("  (Sin datos suficientes)")
        pausar()
        return

    for i, nombre in enumerate(nombres, 1):
        n_publi = publis.get(nombre, 0) if hasattr(publis, 'get') else 0
        print(f"  {i:>2}.  {nombre}  —  {n_publi} publicaciones")

        # HU 35: títulos por autor
        if hasattr(titulos_s, '__getitem__') and nombre in titulos_s:
            for titulo in list(titulos_s[nombre])[:3]:
                print(f"        · {textwrap.shorten(str(titulo), width=56, placeholder='…')}")
        print()
    pausar()


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 8: UNIVERSIDADES  (HU 16–18, 37–38)
# ══════════════════════════════════════════════════════════════════════════════

def flujo_universidades():
    if not requiere_archivo():
        return
    while True:
        encabezado()
        print("\n  ── UNIVERSIDADES ──\n")
        print("  [1]  Ranking general de universidades         (HU 16)")
        print("  [2]  Artículos agrupados por universidad      (HU 17)")
        print("  [3]  Filtrar universidades por país           (HU 18)")
        print("  [4]  Top 10 universidades más activas         (HU 37–38)")
        print("  [0]  Volver al menú principal")

        op = input("\n  Opción: ").strip()

        if op == '':
            continue
        elif op == '0':
            break

        elif op == '1':
            ranking = obtener_ranking_universidades(df)
            if ranking.empty:
                print("\n  (Sin datos de afiliación)")
            else:
                print(f"\n  (Mostrando 20 de {len(ranking)})\n")
                mostrar_tabla(
                    ranking.head(20).values.tolist(),
                    list(ranking.columns),
                    anchos=[50, 14]
                )

        elif op == '2':
            agrupados = obtener_articulos_agrupados_por_universidad(df)
            if agrupados.empty:
                print("\n  (Sin datos)")
            else:
                print(f"\n  Total de instituciones: {len(agrupados)}")
                print("  (Mostrando las primeras 5, con hasta 2 títulos cada una)\n")
                for _, row in agrupados.head(5).iterrows():
                    nombre_inst = textwrap.shorten(
                        str(row['Universidad_Institucion']), width=56, placeholder='…'
                    )
                    print(f"  ▸  {nombre_inst}")
                    for t in list(row['Lista_De_Titulos'])[:2]:
                        lineas = textwrap.wrap(str(t), width=60)
                        print(f"       · {lineas[0]}")
                        for linea in lineas[1:]:
                            print(f"         {linea}")
                    print()

        elif op == '3':
            pais = input("\n  País a buscar (en inglés, ej. Mexico): ").strip()
            resultado = filtrar_universidades_por_pais(df, pais)
            if resultado.empty:
                print(f"\n  No se encontraron universidades para '{pais}'.")
            else:
                print(f"\n  Universidades encontradas en '{pais}': {len(resultado)}\n")
                mostrar_tabla(
                    resultado.head(15).values.tolist(),
                    list(resultado.columns),
                    anchos=[50, 14]
                )

        elif op == '4':
            top = obtener_top_10_universidades_citadas(df)
            if top.empty:
                print("\n  (Sin datos suficientes)")
            else:
                print("\n")
                mostrar_tabla(
                    top.values.tolist(),
                    list(top.columns),
                    anchos=[42, 14, 14]
                )
        else:
            print("\n  Opción inválida.")

        pausar()


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 9: TOP 10 TRABAJOS MÁS RELEVANTES  (HU 45, 46, 48)
# ══════════════════════════════════════════════════════════════════════════════

def flujo_top10_trabajos():
    if not requiere_archivo():
        return
    encabezado()
    print("\n  ── TOP 10 TRABAJOS MÁS RELEVANTES  (HU 45, 46, 48) ──\n")

    if 'DOI' not in df.columns:
        print("  ⚠  La columna 'DOI' no está disponible; se mostrará 'Sin DOI'.")

    lista = top_10_trabajos(df)
    if not lista:
        print("  (Sin datos)")
        pausar()
        return

    for i, (ref, citas, year, doi) in enumerate(lista, 1):
        print(f"  {i:>2}.  [{citas} citas  |  Año: {year}]")
        for linea in textwrap.wrap(ref, width=66):
            print(f"       {linea}")
        print(f"       DOI: {doi}")
        print()
    pausar()


# ══════════════════════════════════════════════════════════════════════════════
# MENÚ PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

MENU_BASE = [
    ("1", "Cargar archivo CSV", flujo_carga),
    ("0", "Salir", None),
]

MENU_COMPLETO = [
    ("1",  "Cargar otro archivo CSV",                         flujo_carga),
    ("",   "── Productividad ─────────────────────────────",  None),
    ("2",  "Métricas generales de productividad  (HU 6–9)",   flujo_productividad),
    ("",   "── Autoría ────────────────────────────────────",  None),
    ("3",  "Estadísticas de autoría  (HU 11–14)",             flujo_autoria),
    ("4",  "Top 10 autores más productivos  (HU 33–35)",      flujo_top_autores),
    ("",   "── Países ─────────────────────────────────────",  None),
    ("5",  "Lista de países  (HU 20–22)",                     flujo_paises),
    ("",   "── Universidades ──────────────────────────────",  None),
    ("6",  "Universidades y filtros  (HU 16–18, 37–38)",      flujo_universidades),
    ("",   "── Impacto ────────────────────────────────────",  None),
    ("7",  "Trabajos más citados en APA  (HU 24)",            flujo_trabajos_citados),
    ("8",  "Promedio de citas anual  (HU 29–31)",             flujo_promedio_citas),
    ("9",  "Top 10 trabajos más relevantes  (HU 45–48)",      flujo_top10_trabajos),
    ("",   "───────────────────────────────────────────────",  None),
    ("0",  "Salir",                                           None),
]


def menu():
    while True:
        encabezado()
        opciones = MENU_COMPLETO if df is not None else MENU_BASE

        print()
        mapa = {}
        for clave, descripcion, func in opciones:
            if clave:
                print(f"  [{clave}]  {descripcion}")
                mapa[clave] = func
            else:
                print(f"  {descripcion}")

        op = input("\n  Opción: ").strip()

        if op == '':
            continue
        elif op == '0':
            print("\n  Hasta luego.\n")
            break
        elif op in mapa:
            func = mapa[op]
            if func is not None:
                func()
        else:
            print("\n  Opción inválida.")
            pausar()


if __name__ == "__main__":
    menu()