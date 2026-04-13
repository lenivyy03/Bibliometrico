import pandas as pd

# Funcion que devuelve el total de publicaciones
def contar_total_publicaciones(df):
    # Verfica si no recibio nada o si el df esta vacio
    if df is None or df.empty:
        return 0
    return len(df)

# Funcion cuenta los autores unicos
def contar_autores_unicos(df):
    # Verifica si no recibio nada o si no tiene una columna de Authors
    if df is None or 'Authors' not in df.columns:
        return 0
    # Crea un conjunto vacio, los conjuntos no permiten duplicados
    autores = set()
    
    # Recorre cada celda de la columna, ignorando las vacias
    for entrada in df['Authors'].dropna():
        # Detecta si los autores estan separados por ; o ,
        sep = ';' if ';' in entrada else ','

        # Divide la celda en autores individuales, elimina los espacios con .strip() y los agrega al conjunto
        autores.update(autor.strip() for autor in entrada.split(sep))

    return len(autores)

# Funcion que cuenta los articulos escritos por un solo autor
def contar_articulos_autor_unico(df):
    # Verifica si no recibio nada o si no tiene una columna de Authors
    if df is None or 'Authors' not in df.columns:
        return 0
    
    # Funcion interna que se usará para evaluar cada celda
    def tiene_un_autor(entrada):
        # Detecta si los autores estan separados por ; o ,
        sep = ';' if ';' in entrada else ','

        # regresa True si al dividir la celda solo hay un autor, False si hay mas 
        return len(entrada.split(sep)) == 1

    # Aplica la funcion a cada celda, haciendo una columna de True/False
    return df['Authors'].dropna().apply(tiene_un_autor).sum()

# Funcion que devuelve un dict con las metricas de productividad 
def metricas_prod(df):
    if df is None:
        print("Error: No hay datos para calcular métricas.")
        return {}

    # NOTA: Esto puede cambiar luego cuando implementemos la interfaz ---
    return {
        "Total de publicaciones": contar_total_publicaciones(df),
        "Autores únicos": contar_autores_unicos(df),
        "Artículos de un solo autor": contar_articulos_autor_unico(df),
    }