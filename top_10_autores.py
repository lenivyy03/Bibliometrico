# Función que regresa información sobre los autores mas destacados

def top_autores(df,tipo):

    # Eliminamos aquellas colummas que tengan celdas vacías en alguna de las columnas
    df = df.dropna(subset=['Author full names', 'Title'])

    # Separemos los nombres de autores en una lista como ['nom1 (ID)','nom2 (ID)','nom3 (ID)'] en la columna de nombres completos
    df['Author full names'] = df['Author full names'].str.split(';')

    # Hacemos que cada autor tenga su propia fila
    df = df.explode('Author full names')

    # Separamos el nombre del ID de la columna dividida de los nombres completos
    temporal = df['Author full names'].str.rsplit("(", n=1, expand=True)

    # Añadimos las columnas que creamos
    df['Nombre_Autor'] = temporal[0].str.strip()
    df['ID_Autor'] = temporal[1].str.replace(")","",regex=False).str.strip()

    # Contamos y agrupamos del mayor al menor, tomamos los primeros 10 y su indice (nombre) 
    top_10_ID = df["ID_Autor"].value_counts().head(10).index

    # Buscamos y guardamos los datos de los primeros 10 IDs mas repetidos
    top_10 = df["ID_Autor"].isin(top_10_ID)

    df_top = df[top_10]

    # Extraemos solo el índice  que contiene los nombres y lo hacemos lista
    if(tipo == 'autores'): return df_top['Nombre_Autor'].value_counts().index.tolist()

    # Pasamos el número de publicaciones
    elif(tipo == 'num_publi'): return df_top['Nombre_Autor'].value_counts()

    # pasamos los trabajos por cada autor
    elif(tipo == 'titulos'): return df_top.groupby("Nombre_Autor")["Title"].unique()
    
    else: return -1
