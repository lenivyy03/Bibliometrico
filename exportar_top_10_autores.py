# Hu 36 exportar top 10 autores
def exportar_top_10_autores(df):
    if df is None: return []
    if 'Author full names' not in df.columns: return []

    # Conseguimos las metricas
    nombres = top_autores(df, 'autores')
    num_publicaciones = top_autores(df, 'num_publi')
    titulos = top_autores(df, 'titulos')

    esqueleto = []
    # Unimos la informacion
    for nom in nombres:
        uniones = { 'Autor': nom, 'Número de artículos': num_publicaciones[nom],
            'Títulos': " | ".join(titulos[nom]) }
        esqueleto.append(uniones)
        
    # Ahora creamos la tabla y exportamos
    df = pd.DataFrame(esqueleto)
    
    nom_archivo = "Los 10 autores más destacados.csv"
    # index como false para evitar la columna de números y el encoding para evitar simbolos extraños
    df.to_csv(nom_archivo, index=False, encoding='utf-8-sig')
     
    print(f"La exportación de los datos se generó como:{nom_archivo}")
    return df
    
