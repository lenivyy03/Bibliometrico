# Función que regresa las estadísticas del número promedio de autores entre todos los articulos
def num_promedio_autores(df):
    # Verificamos que se encuentra información la columna de Autores
    if df is None: return 0
    if 'Authors' not in df.columns: return 0

    # Limpiamos las celdas vacías de la columna de Autores
    documentos = df['Authors'].dropna()

    # Verificamos que después de evitar celdas vacías aun queden celdas validas con autores
    if(documentos.empty): return 0 

    num_autores = 0 # Variable que almacenará la cantidad de autores de toda la recopilación
    
    # Recorremos cada celda de autores ignorando celdas que puedan estar vacías
    for entrada in documentos:
        num_autores += entrada.count(';') + 1 # Contamos el número de autores por celda guiandonos en la separacion de ';' 

    promedio = num_autores/(documentos.count()) # Calculamos el promedio de autores
    return promedio
