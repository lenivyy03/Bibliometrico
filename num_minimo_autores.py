# Función que regresa las estadísticas del menor número de autores que un artículo tuvo entre todos los demas
def num_minimo_autores(df):
    # Verificamos que se encuentra información la columna de Autores
    if df is None: return 0
    if 'Authors' not in df.columns: return 0

    # Limpiamos las celdas vacías de la columna de Autores
    documentos = df['Authors'].dropna()

    # Verificamos que después de evitar celdas vacías aun queden celdas validas con autores
    if(documentos.empty): return 0 
    
    min_autores = 10000 # Establecemos un número exageradamente mayor para obligar la entrada del primer número de autores
    
    # Recorremos cada celda de autores ignorando celdas que puedan estar vacías
    for entrada in documentos:
        num_autores = entrada.count(';') + 1 # Contamos el número de autores por celda guiandonos en la separacion de ';' 
        if(num_autores < min_autores): min_autores = num_autores # Buscamos el número más pequeño de autores entre todos los articulos 
    return min_autores
