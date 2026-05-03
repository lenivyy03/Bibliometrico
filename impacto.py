import pandas as pd


# ─── Referencias APA ──────────────────────────────────────────────────────────

# Función para construir referencias en formato APA a partir de una fila del DataFrame
def construir_referencia_apa(row):
    autores = str(row.get("Authors", "")).strip()
    ano = str(row.get("Year", "")).strip()
    titulo = str(row.get("Title", "")).strip()
    revista = str(row.get("Source title", "")).strip()
    volumen = str(row.get("Volume", "")).strip()
    issue = str(row.get("Issue", "")).strip()
    doi = str(row.get("DOI", "")).strip()
    pagina_inicio = str(row.get("Page start", "")).strip()
    pagina_final = str(row.get("Page end", "")).strip()
    numero_articulo = str(row.get("Art. No.", "")).strip()

    # En caso de tener páginas
    if pagina_inicio and pagina_final:
        paginas_o_articulo = f"{pagina_inicio}-{pagina_final}"
    # En caso de ser un artículo con número
    elif numero_articulo:
        paginas_o_articulo = f"Art. {numero_articulo}"
    # En caso de no tener ninguno
    else:
        paginas_o_articulo = ""

    referencia = f"{autores} ({ano}). {titulo}."

    if revista:
        referencia += f" {revista}"
    if volumen and issue:
        referencia += f", {volumen}({issue})"
    elif volumen:
        referencia += f", {volumen}"
    elif issue:
        referencia += f", ({issue})"

    if paginas_o_articulo:
        referencia += f", {paginas_o_articulo}"

    if doi:
        referencia += f". https://doi.org/{doi}"
    else:
        referencia += "."

    return referencia


# ─── Trabajos más citados (HU 24) ─────────────────────────────────────────────

# Función para generar una lista con los trabajos más citados, ordenada de mayor a menor
def trabajos_mas_citados(df):
    copia = df.copy()
    copia["Cited by"] = pd.to_numeric(copia["Cited by"], errors="coerce").fillna(0)
    copia = copia.sort_values(by=["Cited by"], ascending=False)

    lista_mas_citados = []
    for _, row in copia.iterrows():
        referencia = construir_referencia_apa(row)
        citas = int(row["Cited by"])
        lista_mas_citados.append([referencia, citas])

    return lista_mas_citados


# ─── Promedio de citas anual (HU 29, 30, 31) ──────────────────────────────────

# Función que calcula el promedio de citas anual de cada publicación
def calcular_promedio_citas_anual(df, año_actual=None):
    if año_actual is None:
        año_actual = df['Year'].max()

    df['Cited by'] = df['Cited by'].fillna(0)
    df['Antiguedad'] = año_actual - df['Year'] + 1
    df['Promedio_Citas_Anual'] = df['Cited by'] / df['Antiguedad']
    df['Promedio_Citas_Anual'] = df['Promedio_Citas_Anual'].round(2)

    return df


# Función que ordena las publicaciones por promedio de citas anual de mayor a menor
def ordenar_por_promedio_citas(df):
    if 'Promedio_Citas_Anual' not in df.columns:
        df = calcular_promedio_citas_anual(df)

    df_ordenado = df.sort_values(by='Promedio_Citas_Anual', ascending=False)
    columnas_vista = ['Title', 'Year', 'Promedio_Citas_Anual']

    return df_ordenado[columnas_vista]