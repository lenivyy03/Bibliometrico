import pandas as pd

#Función para cargar csv
def cargar_csv(ruta):
    try:
        # Convierte datos tabulares a una estructura manipulables
        df = pd.read_csv(ruta, encoding="utf-8-sig")

        # Cuantos datos fueron cargados
        total = len(df)

        # Mostramos cuantos datos registro el archivo csv
        print(f"Cargando {total} registros")


        # Esta linea es solo para ver que las columnas del csv se vean ->
        # print(df.columns.tolist())

        # Lista de columnas
        columnas_criticas = ["Authors", "Title", "Year", "Cited by", "Affiliations"]
        columnas_opcionales = ["DOI"]

        # Creamos memoria para las columnas faltantes
        columnas_faltantes = []

        for columna in columnas_criticas:
            if columna not in df.columns:
                #Agregamos al array las columnas que faltaron
                columnas_faltantes.append(columna)

        # Si hubo columnas faltantes indicarlo
        if len(columnas_faltantes) > 0:
            print(f"Faltaron las siguientes columnas: {columnas_faltantes}")
            return None

        for columna in columnas_opcionales:
            if columna not in df.columns:
                print(f"Faltaron las siguientes columna: {columna}")

        #Imprimir las primeras 5 Filas, por ahora se muestran en terminal
        print(df.head())

        # Regresamos el archivo
        return df

    # En caso de no encontrar un archivo mandamos una advertencia
    except FileNotFoundError:
        print("El archivo no existe")
    except Exception as e:
        print(f"Ocurrió un error: {e}")


resultado = cargar_csv("scopus.csv")

