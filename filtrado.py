import pandas as pd
import numpy as np

#Función para ver las estadísticas de autoría agrupadas en una tabla comparativa
def tabla_comparativa_autoria(df):
    
    # Filtrar solo las filas que tengan tanto afiliación como IDs de autores válidos
    datos_validos = df.dropna(subset=['Affiliations', 'Author(s) ID']).copy()
    
    # Calcular cuántos autores tiene cada artículo contando los separadores ';'
    datos_validos['Num_Autores'] = datos_validos['Author(s) ID'].apply(
        lambda x: len(str(x).split(';'))
    )
    
    # Saber si el artículo es individual o en equipo
    datos_validos['Un_Autor'] = np.where(datos_validos['Num_Autores'] == 1, 1, 0)
    datos_validos['Multi_Autor'] = np.where(datos_validos['Num_Autores'] > 1, 1, 0)
    
    # Separar el texto de afiliaciones en una lista
    datos_validos['Lista_Afiliaciones'] = datos_validos['Affiliations'].apply(
        lambda x: [afil.strip() for afil in str(x).split(';') if afil.strip()]
    )
    
    # Explotar la lista para analizar cada institución de forma individual
    afiliaciones_individuales = datos_validos.explode('Lista_Afiliaciones')
    
    # Evitar contar doble una misma universidad en un mismo artículo
    afiliaciones_sin_repetir = afiliaciones_individuales.drop_duplicates(
        subset=['EID', 'Lista_Afiliaciones']
    ).copy()
    
    # Agrupar las estadísticas por universidad
    estadisticas_autoria = afiliaciones_sin_repetir.groupby('Lista_Afiliaciones').agg(
        Total_Articulos=('EID', 'count'),
        Promedio_Autores=('Num_Autores', 'mean'),
        Maximo_Autores=('Num_Autores', 'max'),
        Total_Individuales=('Un_Autor', 'sum'),
        Total_Colaborativos=('Multi_Autor', 'sum')
    ).reset_index()
    
    # Redondear el promedio para que la tabla sea fácil de leer
    estadisticas_autoria['Promedio_Autores'] = estadisticas_autoria['Promedio_Autores'].round(2)
    
    # Renombrar columnas para la salida final
    estadisticas_autoria = estadisticas_autoria.rename(
        columns={'Lista_Afiliaciones': 'Universidad_Institucion'}
    )
    
    # Ordenar del que tiene más artículos al que tiene menos
    estadisticas_autoria = estadisticas_autoria.sort_values(
        by='Total_Articulos', ascending=False
    )
    
    return estadisticas_autoria

# Función que ordena las universidades por número de artículos en los que participan sus autores
def obtener_ranking_universidades(datos_resultados):

    # Eliminar filas que no tengan información de afiliación y hacer una copia
    datos_validos = datos_resultados.dropna(subset=['Affiliations']).copy()
    
    # Convertir el texto separado por ';' en una lista de instituciones
    datos_validos['Lista_Afiliaciones'] = datos_validos['Affiliations'].apply(
        lambda afiliacion: [afil.strip() for afil in str(afiliacion).split(';') if afil.strip()]
    )
    
    # Separamos las universidades que trabajan en un mismo artículo, creando una fila independiente para cada una
    afiliaciones_individuales = datos_validos.explode('Lista_Afiliaciones')
    
    # Eliminar duplicados por Artículo y Universidad para que si una universidad aparece
    # varias veces en el mismo artículo, solo se cuente una vez
    afiliaciones_sin_repetir = afiliaciones_individuales.drop_duplicates(
        subset=['EID', 'Lista_Afiliaciones']
    )
    
    # Contar en cuántos artículos únicos aparece cada institución y ordenar de mayor a menor
    ranking_universidades = afiliaciones_sin_repetir['Lista_Afiliaciones'].value_counts().reset_index()
    ranking_universidades.columns = ['Universidad_Institucion', 'Numero_Articulos']
    
    return ranking_universidades


# Función que ayuda a ver qué artículos corresponden a cada universidad
# Agrupa todos los artículos de una universidad en un
# solo arreglo, ejemplo: UNISON -> ["Articulo1", "Articulo2"]
def obtener_articulos_agrupados_por_universidad(datos_resultados):
    
    # Limpiar datos nulos en afiliaciones y títulos
    datos_validos = datos_resultados.dropna(subset=['Affiliations', 'Title']).copy()
    
    # Convertir el texto separado por ';' en una lista de instituciones limpias
    datos_validos['Lista_Afiliaciones'] = datos_validos['Affiliations'].apply(
        lambda afiliacion: [afil.strip() for afil in str(afiliacion).split(';') if afil.strip()]
    )
    
    # Explotar y eliminar duplicados 
    afiliaciones_individuales = datos_validos.explode('Lista_Afiliaciones')
    afiliaciones_sin_repetir = afiliaciones_individuales.drop_duplicates(
        subset=['EID', 'Lista_Afiliaciones']
    )
    
    # Renombrar la columna antes de ordenar
    afiliaciones_sin_repetir = afiliaciones_sin_repetir.rename(
        columns={'Lista_Afiliaciones': 'Universidad_Institucion'}
    )
    
    # Ordenar para que los artículos más recientes queden primero en la lista final
    afiliaciones_ordenadas = afiliaciones_sin_repetir.sort_values(
        by=['Universidad_Institucion', 'Year'], ascending=[True, False]
    )
    
    # Agrupar por universidad y convertir los títulos en una lista
    articulos_por_universidad = afiliaciones_ordenadas.groupby('Universidad_Institucion')['Title'].apply(list).reset_index()
    articulos_por_universidad.rename(columns={'Title': 'Lista_De_Titulos'}, inplace=True)
    
    return articulos_por_universidad

#Función para filtrar la lista de universidades por país
def filtrar_universidades_por_pais(df, pais_buscado):

    afiliaciones_validas = df.dropna(subset=['Affiliations']).copy()

    afiliaciones_validas['Lista_Afiliaciones'] = afiliaciones_validas['Affiliations'].apply(
        lambda x: [afil.strip() for afil in str(x).split(';') if afil.strip()]
    )

    # Explotar la lista para analizar cada institución de forma individual
    afiliaciones_individuales = afiliaciones_validas.explode('Lista_Afiliaciones')

    afiliaciones_sin_repetir = afiliaciones_individuales.drop_duplicates(
        subset=['EID', 'Lista_Afiliaciones']
    ).copy()

    # Buscamos el nombre del país después de la ultima coma 
    afiliaciones_sin_repetir['Pais'] = afiliaciones_sin_repetir['Lista_Afiliaciones'].apply(
        lambda x: x.split(',')[-1].strip()
    )

    # Filtrar por el país deseado
    universidades_pais = afiliaciones_sin_repetir[
        afiliaciones_sin_repetir['Pais'].str.lower() == pais_buscado.lower()
    ]

    # Contar los artículos de las universidades de ese país
    ranking_universidades = universidades_pais['Lista_Afiliaciones'].value_counts().reset_index()

    ranking_universidades.columns = ['Universidad_Institucion', 'Numero_Articulos']

    return ranking_universidades

#Función para ver las 10 universidades con mayor presencia en los recopilados
def obtener_top_10_universidades_citadas(
    datos_resultados, 
    pais_buscado=None, 
    year_inicio=None, 
    year_fin=None, 
    citas_totales_minimas=None, 
    citas_totales_maximas=None,
    top_n=10 # Servirá para pedir el top 10
):
    # Limpieza de datos
    datos_validos = datos_resultados.dropna(subset=['Affiliations', 'Year', 'Cited by']).copy()
    
    datos_validos['Year'] = pd.to_numeric(datos_validos['Year'], errors='coerce')
    datos_validos['Cited by'] = pd.to_numeric(datos_validos['Cited by'], errors='coerce').fillna(0)
    
    # Filtrar por año
    if year_inicio is not None:
        datos_validos = datos_validos[datos_validos['Year'] >= year_inicio]
    if year_fin is not None:
        datos_validos = datos_validos[datos_validos['Year'] <= year_fin]
        
    if datos_validos.empty:
        return pd.DataFrame(columns=['Universidad_Institucion', 'Numero_Articulos', 'Citas_Totales'])

    datos_validos['Lista_Afiliaciones'] = datos_validos['Affiliations'].apply(
        lambda afiliacion: [aff.strip() for aff in str(afiliacion).split(';') if aff.strip()]
    )
    
    afiliaciones_individuales = datos_validos.explode('Lista_Afiliaciones')
    afiliaciones_sin_repetir = afiliaciones_individuales.drop_duplicates(
        subset=['EID', 'Lista_Afiliaciones']
    ).copy()
    
    # Filtro de país
    if pais_buscado is not None:
        afiliaciones_sin_repetir['Pais'] = afiliaciones_sin_repetir['Lista_Afiliaciones'].apply(
            lambda x: str(x).split(',')[-1].strip()
        )
        afiliaciones_sin_repetir = afiliaciones_sin_repetir[
            afiliaciones_sin_repetir['Pais'].str.lower() == pais_buscado.lower()
        ]
        
    # Agrupar y calcular totales por Universidad
    ranking_filtrado = afiliaciones_sin_repetir.groupby('Lista_Afiliaciones').agg(
        Numero_Articulos=('EID', 'count'),
        Citas_Totales=('Cited by', 'sum')
    ).reset_index()
    
    ranking_filtrado = ranking_filtrado.rename(columns={'Lista_Afiliaciones': 'Universidad_Institucion'})
    
    # Filtro de citas 
    if citas_totales_minimas is not None:
        ranking_filtrado = ranking_filtrado[ranking_filtrado['Citas_Totales'] >= citas_totales_minimas]
        
    if citas_totales_maximas is not None:
        ranking_filtrado = ranking_filtrado[ranking_filtrado['Citas_Totales'] <= citas_totales_maximas]
        
    # Ordenamos de la más citada a la menos citada
    ranking_filtrado = ranking_filtrado.sort_values(by='Citas_Totales', ascending=False)
    
    # Extraemos únicamente los primeros 10 lugares (top_n = 10)
    top_10_final = ranking_filtrado.head(top_n)
    
    return top_10_final
