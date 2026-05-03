import os
import pandas as pd

# La HU 55 (Crear un proyecto) es logicamente igual
# HU 56: Guardar un proyecto
def guardar_proyecto(df, nombre_proyecto):
    # Creamos la carpeta si no existe
    os.makedirs("proyectos_guardados", exist_ok=True)
    # Construímos la ruta
    ruta = os.path.join("proyectos_guardados", nombre_proyecto + ".pkl")
    # Guardamos el DataFrame en un archivo pickle
    df.to_pickle(ruta)

# HU 57: Abrir un proyecto guardado
def abrir_proyecto(nombre_proyecto):
    # Construímos la ruta
    ruta = os.path.join("proyectos_guardados", nombre_proyecto + ".pkl")
    # Abrimos el archivo pickle del DataFrame
    df = pd.read_pickle(ruta)
    return df

# HU 58: Lista de proyectos existentes al iniciar la aplicación
def listar_proyectos():
    # Si no hay proyectos, devolver lista vacía
    if not os.path.exists('proyectos_guardados'):
        return []

    # Lista con los nombres crudos de todos los proyectos
    archivos = os.listdir("proyectos_guardados")
    # Lista con los nombres limpios de todos los proyectos
    nombres_proyectos = [nombre.removesuffix(".pkl")  for nombre in archivos]
    return nombres_proyectos