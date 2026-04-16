import pandas as pd

# Funcion para generar una lista con los trabajos mas citados
def trabajos_mas_citados(df):
    # Hacemos una copia del dataframe
    copia = df.copy()

    # Convertimos los valores a numeros
    copia["Cited by"] = pd.to_numeric(copia["Cited by"], errors="coerce").fillna(0)

    # Ordenamos la columna de mayor a menor
    copia = copia.sort_values(by=["Cited by"], ascending=False)

    lista_mas_citados = []

    for index, row in copia.iterrows():
        referencia = construir_referencia_apa(row)
        citas = int(row["Cited by"])
        lista_mas_citados.append([referencia, citas])

    return lista_mas_citados


# Funcion para construir referencias apa
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

    # En caso de tener paginas
    if pagina_inicio and pagina_final:
        paginas_o_articulo = f"{pagina_inicio}-{pagina_final}"
    # En caso de ser un articulo
    elif numero_articulo:
        paginas_o_articulo = f"Art. {numero_articulo}"
    # En caso de no tener ninguno
    else:
        paginas_o_articulo = ""

    referencia = f"{autores} ({ano}). {titulo}."

    # Checa que las columnas apas esten disponibles para usarse.
    if revista:
        referencia += f" {revista}"
    if volumen and issue:
        referencia += f", {volumen}({issue})"
    elif volumen:
        referencia += f", {volumen}"
    elif issue:
        referencia += f", ({issue})"

    # Para mejor redacción
    if paginas_o_articulo:
        referencia += f", {paginas_o_articulo}"

    if doi:
        referencia += f". https://doi.org/{doi}"
    else:
        referencia += "."

    return referencia

