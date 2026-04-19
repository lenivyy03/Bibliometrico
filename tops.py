import pandas as pd
from impacto import construir_referencia_apa

# Módulo consolidado de tops (HU 33, 34, 35, 45, 46, 48)
# Fusiona: top_10.py, top_10_autores.py


# ─── Top 10 trabajos más citados ──────────────────────────────────────────────
# Devuelve los datos suficientes para las HU 45, 46 y 48
# Cada elemento de la lista es: [referencia_apa, num_citas, año, doi]
def top_10_trabajos(df):
    copia = df.copy()
    copia["Cited by"] = pd.to_numeric(copia["Cited by"], errors="coerce").fillna(0)

    top_10 = copia.sort_values(by=["Cited by"], ascending=False).head(10)
    lista_top10 = []

    for _, row in top_10.iterrows():
        referencia = construir_referencia_apa(row)
        citas = int(row["Cited by"])
        year = row.get("Year", "N/A")
        doi = row.get("DOI", "")
        doi = doi if pd.notna(doi) and str(doi).strip() else "Sin DOI"
        lista_top10.append([referencia, citas, year, doi])

    return lista_top10


# ─── Top 10 autores más productivos ──────────────────────────────────────────
# tipo='autores'   → lista de nombres ordenados por publicaciones
# tipo='num_publi' → Series con nombre → número de publicaciones
# tipo='titulos'   → Series con nombre → array de títulos únicos
def top_autores(df, tipo):
    df = df.dropna(subset=['Author full names', 'Title']).copy()

    # Separar los autores en una lista: ['nom1 (ID)', 'nom2 (ID)', ...]
    df['Author full names'] = df['Author full names'].str.split(';')

    # Una fila por autor
    df = df.explode('Author full names')

    # Separar nombre e ID del formato "Apellido, Nombre (ID)"
    temporal = df['Author full names'].str.rsplit("(", n=1, expand=True)
    df['Nombre_Autor'] = temporal[0].str.strip()
    df['ID_Autor'] = temporal[1].str.replace(")", "", regex=False).str.strip()

    # Contamos publicaciones por ID (un ID = un autor en Scopus)
    conteo_por_id = df["ID_Autor"].value_counts().head(10)
    top_10_IDs = conteo_por_id.index
    df_top = df[df["ID_Autor"].isin(top_10_IDs)].copy()

    # El mismo autor puede aparecer con distintas grafías del nombre según el artículo.
    # Elegimos el nombre más frecuente por ID (nombre canónico) para mostrar solo uno.
    nombre_canonico = (
        df_top.groupby("ID_Autor")["Nombre_Autor"]
        .agg(lambda x: x.value_counts().index[0])
    )

    # Los IDs ya están ordenados de mayor a menor publicaciones
    ids_ordenados = conteo_por_id.index.tolist()

    if tipo == 'autores':
        return [nombre_canonico[id_] for id_ in ids_ordenados]

    elif tipo == 'num_publi':
        # Serie: nombre canónico → número de publicaciones
        return pd.Series(
            {nombre_canonico[id_]: conteo_por_id[id_] for id_ in ids_ordenados}
        )

    elif tipo == 'titulos':
        # Serie: nombre canónico → array de títulos únicos
        return pd.Series(
            {nombre_canonico[id_]: df_top[df_top["ID_Autor"] == id_]["Title"].unique()
             for id_ in ids_ordenados}
        )

    else:
        return -1