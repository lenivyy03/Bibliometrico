import pandas as pd
import numpy as np


def _extraer_pais(afiliacion_str: str) -> str:
    """Extrae el nombre del país de una afiliación individual de Scopus.

    Scopus usa el formato: 'Dept., Universidad, Ciudad, País'.
    El país es siempre el último elemento separado por coma, PERO algunos
    registros terminan en código postal o están vacíos — esta función los
    descarta buscando desde el final hasta encontrar un token no numérico.
    """
    partes = [p.strip() for p in str(afiliacion_str).split(',')]
    for parte in reversed(partes):
        # Ignorar vacíos y cadenas que sean solo dígitos / códigos postales
        if parte and not parte.replace('-', '').replace(' ', '').isdigit():
            return parte
    return ''


# Función auxiliar (no es ninguna historia), ayuda a quitar el problema de que el nombre de la universidad aparezca
# junto al nombre del país, es decir, solo extrae el nombre de la universidad
def extraer_nombre_universidad(afiliacion_completa):

    # Separar por comas y limpiar espacios
    partes = [p.strip() for p in str(afiliacion_completa).split(',')]
    
    # Palabras clave que identifican a la institución principal
    palabras_clave = [
        'university', 'universidad', 'institute', 'instituto', 
        'college', 'school', 'escuela', 'polytechnic', 'politécnico',
        'academy', 'academia', 'facultad', 'faculty', 'hospital', 'center', 'centro'
    ]
    
    # Buscar la parte que contenga alguna de las palabras clave
    for parte in partes:
        if any(palabra in parte.lower() for palabra in palabras_clave):
            return parte
            
    # Si no hay palabra clave, la institución suele ser el primer elemento
    return partes[0] if partes else afiliacion_completa.strip()

#Función para ver las estadísticas de autoría agrupadas en una tabla comparativa
def tabla_comparativa_autoria(df):
    
    datos_validos = df.dropna(subset=['Affiliations', 'Author(s) ID']).copy()
    
    datos_validos['Num_Autores'] = datos_validos['Author(s) ID'].apply(lambda x: len(str(x).split(';')))
    datos_validos['Un_Autor'] = np.where(datos_validos['Num_Autores'] == 1, 1, 0)
    datos_validos['Multi_Autor'] = np.where(datos_validos['Num_Autores'] > 1, 1, 0)
    
    datos_validos['Lista_Afiliaciones'] = datos_validos['Affiliations'].apply(
        lambda x: [afil.strip() for afil in str(x).split(';') if afil.strip()]
    )
    
    afiliaciones_individuales = datos_validos.explode('Lista_Afiliaciones')
    
    # Aplicar la funcion de extraccion del nombre de la universidad
    afiliaciones_individuales['Universidad_Institucion'] = afiliaciones_individuales['Lista_Afiliaciones'].apply(extraer_nombre_universidad)
    
    # Evitar contar doble una misma universidad
    afiliaciones_sin_repetir = afiliaciones_individuales.drop_duplicates(
        subset=['EID', 'Universidad_Institucion']
    ).copy()
    
    # Agrupar las estadísticas usando el nombre limpio
    estadisticas_autoria = afiliaciones_sin_repetir.groupby('Universidad_Institucion').agg(
        Total_Articulos=('EID', 'count'),
        Promedio_Autores=('Num_Autores', 'mean'),
        Maximo_Autores=('Num_Autores', 'max'),
        Total_Individuales=('Un_Autor', 'sum'),
        Total_Colaborativos=('Multi_Autor', 'sum')
    ).reset_index()
    
    estadisticas_autoria['Promedio_Autores'] = estadisticas_autoria['Promedio_Autores'].round(2)
    estadisticas_autoria = estadisticas_autoria.sort_values(by='Total_Articulos', ascending=False)
    
    return estadisticas_autoria

# Función que ordena las universidades por número de artículos en los que participan sus autores
def obtener_ranking_universidades(datos_resultados):

    datos_validos = datos_resultados.dropna(subset=['Affiliations']).copy()
    
    datos_validos['Lista_Afiliaciones'] = datos_validos['Affiliations'].apply(
        lambda afiliacion: [afil.strip() for afil in str(afiliacion).split(';') if afil.strip()]
    )
    
    afiliaciones_individuales = datos_validos.explode('Lista_Afiliaciones')
    
    # Aplicar la funcion de extraccion del nombre de la universidad
    afiliaciones_individuales['Universidad_Institucion'] = afiliaciones_individuales['Lista_Afiliaciones'].apply(extraer_nombre_universidad)
    
    # Borrar duplicados por EID y Universidad
    afiliaciones_sin_repetir = afiliaciones_individuales.drop_duplicates(
        subset=['EID', 'Universidad_Institucion']
    )
    
    ranking_universidades = afiliaciones_sin_repetir['Universidad_Institucion'].value_counts().reset_index()
    ranking_universidades.columns = ['Universidad_Institucion', 'Numero_Articulos']
    
    return ranking_universidades


# Función que ayuda a ver qué artículos corresponden a cada universidad
def obtener_articulos_agrupados_por_universidad(datos_resultados):
    
    datos_validos = datos_resultados.dropna(subset=['Affiliations', 'Title']).copy()
    
    datos_validos['Lista_Afiliaciones'] = datos_validos['Affiliations'].apply(
        lambda afiliacion: [afil.strip() for afil in str(afiliacion).split(';') if afil.strip()]
    )
    
    afiliaciones_individuales = datos_validos.explode('Lista_Afiliaciones')
    
    # Aplicar la funcion de extraccion del nombre de la universidad
    afiliaciones_individuales['Universidad_Institucion'] = afiliaciones_individuales['Lista_Afiliaciones'].apply(extraer_nombre_universidad)
    
    # Borrar duplicados
    afiliaciones_sin_repetir = afiliaciones_individuales.drop_duplicates(
        subset=['EID', 'Universidad_Institucion']
    )
    
    afiliaciones_ordenadas = afiliaciones_sin_repetir.sort_values(
        by=['Universidad_Institucion', 'Year'], ascending=[True, False]
    )
    
    articulos_por_universidad = afiliaciones_ordenadas.groupby('Universidad_Institucion')['Title'].apply(list).reset_index()
    articulos_por_universidad.rename(columns={'Title': 'Lista_De_Titulos'}, inplace=True)
    
    return articulos_por_universidad

#Función para filtrar la lista de universidades por país
def filtrar_universidades_por_pais(df, pais_buscado):

    afiliaciones_validas = df.dropna(subset=['Affiliations']).copy()

    afiliaciones_validas['Lista_Afiliaciones'] = afiliaciones_validas['Affiliations'].apply(
        lambda x: [afil.strip() for afil in str(x).split(';') if afil.strip()]
    )

    afiliaciones_individuales = afiliaciones_validas.explode('Lista_Afiliaciones')

    # Obtenemos el país de la cadena original primero
    afiliaciones_individuales['Pais'] = afiliaciones_individuales['Lista_Afiliaciones'].apply(
        _extraer_pais
    )
    
    # Aplicar la funcion de extraccion del nombre de la universidad
    afiliaciones_individuales['Universidad_Institucion'] = afiliaciones_individuales['Lista_Afiliaciones'].apply(extraer_nombre_universidad)

    afiliaciones_sin_repetir = afiliaciones_individuales.drop_duplicates(
        subset=['EID', 'Universidad_Institucion']
    ).copy()

    # Filtrar por el país deseado
    universidades_pais = afiliaciones_sin_repetir[
        afiliaciones_sin_repetir['Pais'].str.lower() == pais_buscado.lower()
    ]

    ranking_universidades = universidades_pais['Universidad_Institucion'].value_counts().reset_index()
    ranking_universidades.columns = ['Universidad_Institucion', 'Numero_Articulos']

    return ranking_universidades

#Función para ver las 10 universidades con mayor presencia en los recopilados
def obtener_top_10_universidades_citadas(
    datos_resultados, pais_buscado=None, year_inicio=None, year_fin=None, 
    citas_totales_minimas=None, citas_totales_maximas=None, top_n=10
):
    datos_validos = datos_resultados.dropna(subset=['Affiliations', 'Year', 'Cited by']).copy()
    
    datos_validos['Year'] = pd.to_numeric(datos_validos['Year'], errors='coerce')
    datos_validos['Cited by'] = pd.to_numeric(datos_validos['Cited by'], errors='coerce').fillna(0)
    
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
    
    # País original
    afiliaciones_individuales['Pais'] = afiliaciones_individuales['Lista_Afiliaciones'].apply(
        _extraer_pais
    )

    # Aplicar la funcion de extraccion del nombre de la universidad
    afiliaciones_individuales['Universidad_Institucion'] = afiliaciones_individuales['Lista_Afiliaciones'].apply(extraer_nombre_universidad)
    
    afiliaciones_sin_repetir = afiliaciones_individuales.drop_duplicates(
        subset=['EID', 'Universidad_Institucion']
    ).copy()
    
    # Filtro de país
    if pais_buscado is not None:
        afiliaciones_sin_repetir = afiliaciones_sin_repetir[
            afiliaciones_sin_repetir['Pais'].str.lower() == pais_buscado.lower()
        ]
        
    ranking_filtrado = afiliaciones_sin_repetir.groupby('Universidad_Institucion').agg(
        Numero_Articulos=('EID', 'count'),
        Citas_Totales=('Cited by', 'sum')
    ).reset_index()
    
    if citas_totales_minimas is not None:
        ranking_filtrado = ranking_filtrado[ranking_filtrado['Citas_Totales'] >= citas_totales_minimas]
    if citas_totales_maximas is not None:
        ranking_filtrado = ranking_filtrado[ranking_filtrado['Citas_Totales'] <= citas_totales_maximas]
        
    ranking_filtrado = ranking_filtrado.sort_values(by='Citas_Totales', ascending=False)
    
    return ranking_filtrado.head(top_n)


# Historia 39: Ver a qué país pertenece cada universidad del top 10
def obtener_pais_universidades_top_10(datos_resultados):
    """Devuelve el país más frecuente para CADA universidad del corpus.

    El diccionario resultante se usa para enriquecer el top 10 filtrado por
    citas, que puede incluir instituciones que no son top-10 por artículos.
    Por eso ya no se limita a 10 filas: se mapean todas las universidades.
    """
    datos_validos = datos_resultados.dropna(subset=['Affiliations']).copy()

    datos_validos['Lista_Afiliaciones'] = datos_validos['Affiliations'].apply(
        lambda afiliacion: [afil.strip() for afil in str(afiliacion).split(';') if afil.strip()]
    )

    afiliaciones_individuales = datos_validos.explode('Lista_Afiliaciones')

    afiliaciones_individuales['Pais'] = afiliaciones_individuales['Lista_Afiliaciones'].apply(
        _extraer_pais
    )
    afiliaciones_individuales['Universidad_Institucion'] = afiliaciones_individuales['Lista_Afiliaciones'].apply(
        extraer_nombre_universidad
    )

    # Solo filas donde se extrajo un país válido
    con_pais = afiliaciones_individuales[afiliaciones_individuales['Pais'] != ''].copy()

    if con_pais.empty:
        return pd.DataFrame(columns=['Universidad_Institucion', 'Pais'])

    # Para cada universidad, el país que aparece con mayor frecuencia
    pais_por_univ = (
        con_pais.groupby('Universidad_Institucion')['Pais']
        .agg(lambda x: x.value_counts().index[0])
        .reset_index()
    )
    pais_por_univ.columns = ['Universidad_Institucion', 'Pais']

    return pais_por_univ

# Historia 42: Función para ver el porcentaje que representa cada país del top 10 sobre el total del corpus
def porcentaje_top_10_paises_corpus(datos_resultados):
    
    # Obtener la cantidad total de artículos únicos en todo el corpus
    total_articulos_corpus = datos_resultados['EID'].nunique()
    
    datos_validos = datos_resultados.dropna(subset=['Affiliations']).copy()
    datos_validos['Lista_Afiliaciones'] = datos_validos['Affiliations'].apply(
        lambda x: [afil.strip() for afil in str(x).split(';') if afil.strip()]
    )
    afiliaciones_individuales = datos_validos.explode('Lista_Afiliaciones')
    
    afiliaciones_individuales['Pais'] = afiliaciones_individuales['Lista_Afiliaciones'].apply(
        _extraer_pais
    )
    
    paises_sin_repetir = afiliaciones_individuales.drop_duplicates(subset=['EID', 'Pais'])
    paises_sin_repetir = paises_sin_repetir[paises_sin_repetir['Pais'] != '']

    ranking_paises = paises_sin_repetir['Pais'].value_counts().reset_index()
    ranking_paises.columns = ['Pais', 'Numero_Articulos']

    # Selecciona el top 10
    top_10_paises = ranking_paises.head(10).copy()
    
    # Calcular el porcentaje que representa sobre el total del corpus
    top_10_paises['Porcentaje_Del_Corpus'] = (top_10_paises['Numero_Articulos'] / total_articulos_corpus) * 100
    
    # Redondear el porcentaje a dos decimales para una mejor presentación
    top_10_paises['Porcentaje_Del_Corpus'] = top_10_paises['Porcentaje_Del_Corpus'].round(2)
    
    return top_10_paises

# Historia 44: Función para ver los 10 países del ranking acompañados de un conteo de sus artículos
def obtener_top_10_paises_articulos(datos_resultados):
    
    # Limpiar datos nulos en las afiliaciones
    datos_validos = datos_resultados.dropna(subset=['Affiliations']).copy()
    
    datos_validos['Lista_Afiliaciones'] = datos_validos['Affiliations'].apply(
        lambda afiliacion: [afil.strip() for afil in str(afiliacion).split(';') if afil.strip()]
    )
    
    # Separar afiliaciones
    afiliaciones_individuales = datos_validos.explode('Lista_Afiliaciones')
    
    # Extraer el país de cada afiliación individual
    afiliaciones_individuales['Pais'] = afiliaciones_individuales['Lista_Afiliaciones'].apply(
        _extraer_pais
    )
    
    # Eliminar duplicados por 'EID' y 'Pais' para que, si dos universidades del mismo país
    # colaboran en un artículo, ese país solo se cuente una vez para dicho artículo
    paises_sin_repetir = afiliaciones_individuales.drop_duplicates(
        subset=['EID', 'Pais']
    )
    paises_sin_repetir = paises_sin_repetir[paises_sin_repetir['Pais'] != '']

    # Contar los artículos por país
    ranking_paises = paises_sin_repetir['Pais'].value_counts().reset_index()
    ranking_paises.columns = ['Pais', 'Numero_Articulos']
    
    # Obtener el top 10 de países
    top_10_paises = ranking_paises.head(10)
    
    return top_10_paises
