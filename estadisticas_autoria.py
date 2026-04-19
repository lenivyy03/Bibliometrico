# Módulo consolidado de estadísticas de autoría (HU 11, 12, 13)
# Fusiona: num_minimo_autores.py, num_maximo_autores.py, num_promedio_autores.py


# Función que regresa el menor número de autores que tuvo un artículo
def num_minimo_autores(df):
    if df is None:
        return -1
    if 'Authors' not in df.columns:
        return -1
    documentos = df['Authors'].dropna()
    if documentos.empty:
        return -1

    min_autores = 10000
    for entrada in documentos:
        num_autores = entrada.count(';') + 1
        if num_autores < min_autores:
            min_autores = num_autores
    return min_autores


# Función que regresa el mayor número de autores que tuvo un artículo
def num_maximo_autores(df):
    if df is None:
        return -1
    if 'Authors' not in df.columns:
        return -1
    documentos = df['Authors'].dropna()
    if documentos.empty:
        return -1

    max_autores = 0
    for entrada in documentos:
        num_autores = entrada.count(';') + 1
        if num_autores > max_autores:
            max_autores = num_autores
    return max_autores


# Función que regresa el promedio de autores entre todos los artículos
def num_promedio_autores(df):
    if df is None:
        return -1
    if 'Authors' not in df.columns:
        return -1
    documentos = df['Authors'].dropna()
    if documentos.empty:
        return -1

    total_autores = 0
    for entrada in documentos:
        total_autores += entrada.count(';') + 1

    promedio = total_autores / documentos.count()
    return promedio
