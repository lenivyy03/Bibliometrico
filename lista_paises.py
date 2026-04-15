import pandas as pd

# Funcion que devuelve una serie con paises de todos los articulos
def extraer_paises(df):
    # Se descartan las filas sin afiliacion, y se crea una serie de Pandas 
    # con todas las posibles "afiliaciones" de un solo articulo
    afiliaciones = df['Affiliations'].dropna().str.split(';').explode()
  
    # En Scopus, la ultima palabra de cada afiliacion individual siempre es el pais.
    # Creamos una serie escogiendo el pais de cada afiliacion, y cuidamos el formato
    paises_limpios = afiliaciones.apply(lambda fila: fila.split(',')[-1].strip())
    return paises_limpios

# Funcion que devuelve una serie con paises y cuantos articulos corresponden a cada uno
def obtener_frecuencias_paises(paises_limpios):
    frecuencias = paises_limpios.value_counts()
    return frecuencias
