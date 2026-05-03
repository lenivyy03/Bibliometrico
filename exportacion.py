#Función para exportar una lista de universidades con sus artículos correspondientes
def exportar_lista_universidades(datos_resultados, nombre_archivo="resultado_bibliometria", formato="csv"):

    # Hacer una copia para no alterar los datos originales
    datos_preparados = datos_resultados.copy()
    
    # Verificamos si hay columnas que contienen listas
    # y las convertimos a una sola cadena de texto separada por " | "
    for columnas in datos_preparados.columns:
        
        # Verificamos el primer elemento para saber si la columna es de tipo lista
        if len(datos_preparados) > 0 and isinstance(datos_preparados[columnas].iloc[0], list):
            
            # Reemplazamos la lista por texto plano
            datos_preparados[columnas] = datos_preparados[columnas].apply(
                lambda lista_valores: " | ".join(map(str, lista_valores))
            )
    
    # Exportar según el formato elegido
    if formato.lower() == "csv":
        archivo_salida = f"{nombre_archivo}.csv"
        # utf-8-sig es para que reconozca la ñ y los acentos
        datos_preparados.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
    
    elif formato.lower() == "xlsx":
        archivo_salida = f"{nombre_archivo}.xlsx"
        datos_preparados.to_excel(archivo_salida, index=False)
    
    else:
        print("Formato no soportado. Elige 'csv' o 'xlsx'.")
        return
        
    print(f"Archivo exportado exitosamente como: {archivo_salida}")
    return archivo_salida

# Historia 40: Función para exportar el ranking de las 10 universidades principales a un documento
def exportar_top_10_universidades(df_top_10_universidades, nombre_archivo="top_10_universidades", formato="csv"):
    
    # Hacer una copia para no alterar los datos de entrada
    datos_exportar = df_top_10_universidades.copy()
    
    # Exportar según el formato 
    if formato.lower() == "csv":
        archivo_salida = f"{nombre_archivo}.csv"
        # utf-8-sig es para reconocer caracteres especiales como ñ y acentos
        datos_exportar.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
        
    elif formato.lower() == "xlsx":
        archivo_salida = f"{nombre_archivo}.xlsx"
        datos_exportar.to_excel(archivo_salida, index=False)
        
    else:
        print("Formato no soportado. Elige 'csv' o 'xlsx'.")
        return None
        
    print(f"Archivo del top 10 exportado exitosamente como: {archivo_salida}")
    return archivo_salida

# Historia 43: Función para exportar el ranking de los 10 países principales exclusivamente a Excel
def exportar_top_10_paises_excel(df_top_10_paises, nombre_archivo="ranking_top_10_paises"):
    
    # Se agrega la extensión .xlsx al nombre del archivo
    archivo_salida = f"{nombre_archivo}.xlsx"
    
    # Guardar los datos en un documento de Excel
    df_top_10_paises.to_excel(archivo_salida, index=False)
    
    print(f"Ranking de países exportado exitosamente a Excel como: {archivo_salida}")
    
    return archivo_salida


# Función para exportar el resumen de conteos a un documento legible
def exportar_resumen_conteos(resumen, nombre_archivo="resumen_conteos", formato="csv"):
    # Verifica que el resumen no este vacio
    if not resumen:
        print("No hay datos de conteo para exportar")
        return None

    # Convierte el diccionario a un DataFrame de dos columnas
    df_resumen = pd.DataFrame(list(resumen.items()), columns=["Metrica", "Valor"])
    
    # Exportar segun el formato elegido
    if formato.lower() == "csv":
        archivo_salida = f"{nombre_archivo}.csv"
        # utf-8-sig es para reconocer caracteres especiales como ñ y acentos
        df_resumen.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
    
    elif formato.lower() == "xlsx":
        archivo_salida = f"{nombre_archivo}.xlsx"
        df_resumen.to_excel(archivo_salida, index=False)
    
    else:
        print("Formato no soportado. Elige 'csv' o 'xlsx'.")
        return None
    
    print(f"Resumen de conteos exportado exitosamente como: {archivo_salida}")
    return archivo_salida

# Función para exportar las estadísticas de autoría con los artículos correspondientes
def exportar_estadisticas_autoria(df, nombre_archivo="estadisticas_autoria", formato="csv"):
    # Verifica si no recibio nada o si no tiene columna de Authors
    if df is None or 'Authors' not in df.columns:
        print("No hay datos de autoría para exportar")
        return None
    
    # Selecciona solo las columnas relevantes para la autoria
    df_autoria = df[['Title', 'Authors', 'Year']].copy()
    
    # Exportar segun el formato elegido
    if formato.lower() == "csv":
        archivo_salida = f"{nombre_archivo}.csv"
        # utf-8-sig es para reconocer caracteres especiales como ñ y acentos
        df_autoria.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
    
    elif formato.lower() == "xlsx":
        archivo_salida = f"{nombre_archivo}.xlsx"
        df_autoria.to_excel(archivo_salida, index=False)

    
    else:
        print("Formato no soportado. Elige 'csv' o 'xlsx'.")
        return None
    
    print(f"Estadísticas de autoría exportadas exitosamente como: {archivo_salida}")
    return archivo_salida

# Función para exportar la lista de promedios de citas anuales a Excel
def exportar_promedios_citas(df, nombre_archivo="promedios_citas"):
    # Verifica si la columna ya fue calculada antes de exportar
    if df is None or 'Promedio_Citas_Anual' not in df.columns:
        print("No hay promedios de citas para exportar, calcula primero el impacto")
        return None
    
    # Selecciona las columnas del ranking y ordena de mayor a menor
    df_exportar = df[['Title', 'Year', 'Promedio_Citas_Anual']].copy()
    df_exportar = df_exportar.sort_values(by='Promedio_Citas_Anual', ascending=False)
    
    # Se agrega la extensión .xlsx al nombre del archivo
    archivo_salida = f"{nombre_archivo}.xlsx"
    df_exportar.to_excel(archivo_salida, index=False)
    
    print(f"Promedios de citas exportados exitosamente como: {archivo_salida}")
    return archivo_salida

# Función para exportar solo las secciones elegidas por el usuario
def exportar_secciones(df, resumen, secciones, nombre_archivo="reporte_personalizado"):
    # Verifica que se haya elegido al menos una seccion
    if not secciones:
        print("No se eligió ninguna sección para exportar")
        return None
    
    archivo_salida = f"{nombre_archivo}.xlsx"
    
    # Crea un escritor de Excel para guardar varias hojas en un solo archivo
    with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
        
        # Exporta cada seccion elegida en su propia hoja
        if 'conteos' in secciones and resumen:
            df_conteos = pd.DataFrame(list(resumen.items()), columns=["Metrica", "Valor"])
            df_conteos.to_excel(writer, sheet_name='Conteos', index=False)
        
        if 'autoria' in secciones and df is not None:
            df[['Title', 'Authors', 'Year']].to_excel(writer, sheet_name='Autoria', index=False)
        
        if 'impacto' in secciones and df is not None and 'Promedio_Citas_Anual' in df.columns:
            df[['Title', 'Year', 'Promedio_Citas_Anual']].to_excel(writer, sheet_name='Impacto', index=False)
    
    print(f"Reporte personalizado exportado exitosamente como: {archivo_salida}")
    return archivo_salida

# Función para exportar referencias en formato APA
def exportar_referencias_apa(df, nombre_archivo="referencias_apa", formato="csv"):
    # Verifica si no recibio nada o si le faltan columnas necesarias para el formato APA
    if df is None or not {'Authors', 'Title', 'Year'}.issubset(df.columns):
        print("Faltan columnas necesarias para generar referencias APA")
        return None
    
    # Construye la referencia APA por fila: Autor(es). (Año). Título.
    df_apa = df.copy()
    df_apa['Referencia_APA'] = (
        df_apa['Authors'].fillna('Sin autor') + '. (' +
        df_apa['Year'].astype(str) + '). ' +
        df_apa['Title'].fillna('Sin título') + '.'
    )
    
    # Agrega el DOI al final de la referencia si existe
    if 'DOI' in df_apa.columns:
        df_apa['Referencia_APA'] += df_apa['DOI'].apply(
            lambda doi: f' https://doi.org/{doi}' if pd.notna(doi) else ''
        )
    
    # Selecciona solo la columna de referencias para el archivo final
    df_exportar = df_apa[['Referencia_APA']].copy()
    
    # Exportar segun el formato elegido
    if formato.lower() == "csv":
        archivo_salida = f"{nombre_archivo}.csv"
        # utf-8-sig es para reconocer caracteres especiales como ñ y acentos
        df_exportar.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
    
    elif formato.lower() == "xlsx":
        archivo_salida = f"{nombre_archivo}.xlsx"
        df_exportar.to_excel(archivo_salida, index=False)
    
    else:
        print("Formato no soportado. Elige 'csv' o 'xlsx'.")
        return None
    
    print(f"Referencias APA exportadas exitosamente como: {archivo_salida}")
    return archivo_salida
