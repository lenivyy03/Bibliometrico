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
