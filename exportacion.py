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
