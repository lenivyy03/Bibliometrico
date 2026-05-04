# HU 41 Top 10 paises con mas publicaciones
def Obtener_paises(afili): # afili = afiliacion
    # Se separa por ;, para cada institucion
    inst = afili.split(';')
    paises = []
    for i in inst:
        partes = i.split(',') # separamos los elementos de cada institucion
        pais = partes[-1].strip() #tomamos el pais y limpiamos posibles espacios
        paises.append(pais)
    return list(set(paises))

def top_paises_publicaciones(df):
    if df is None: return []
    if 'Affiliations' not in df.columns: return []

    afiliaciones = df['Affiliations'].dropna()
    numero_paises = afiliaciones.apply(Obtener_paises).explode().value_counts()
    return numero_paises.head(10)
