import os
import pandas as pd

# HU 55 / 56: Crear y guardar un proyecto
def guardar_proyecto(df, nombre_proyecto):
    os.makedirs("proyectos_guardados", exist_ok=True)
    ruta = os.path.join("proyectos_guardados", nombre_proyecto + ".pkl")
    df_save = df.copy()
    # Normalizar StringDtype extendido → object para evitar incompatibilidades al reabrir
    for col in df_save.columns:
        if df_save[col].dtype != object and pd.api.types.is_string_dtype(df_save[col]):
            try:
                df_save[col] = df_save[col].astype(object)
            except Exception:
                pass
    df_save.to_pickle(ruta)

# HU 57: Abrir un proyecto guardado
def abrir_proyecto(nombre_proyecto):
    import pickle
    ruta = os.path.join("proyectos_guardados", nombre_proyecto + ".pkl")
    try:
        df = pd.read_pickle(ruta)
    except Exception:
        # Fallback: pickle directo para archivos guardados con pandas anterior
        with open(ruta, "rb") as f:
            df = pickle.load(f)
    # Normalizar StringDtype → object
    for col in df.columns:
        if df[col].dtype != object and pd.api.types.is_string_dtype(df[col]):
            try:
                df[col] = df[col].astype(object)
            except Exception:
                df[col] = df[col].astype(str)
    return df

# HU 58: Lista de proyectos existentes al iniciar la aplicación
# HU 60: Fecha de última modificación
def listar_proyectos():
    if not os.path.exists('proyectos_guardados'):
        return []
    from datetime import datetime
    resultado = []
    for archivo in os.listdir("proyectos_guardados"):
        if archivo.endswith(".pkl"):
            ruta = os.path.join("proyectos_guardados", archivo)
            nombre = archivo.removesuffix(".pkl")
            fecha = datetime.fromtimestamp(os.path.getmtime(ruta)).strftime("%Y-%m-%d %H:%M")
            resultado.append((nombre, fecha))
    resultado.sort(key=lambda x: x[1], reverse=True)
    return resultado

# HU 59: Eliminar un proyecto
def eliminar_proyecto(nombre_proyecto):
    ruta = os.path.join("proyectos_guardados", nombre_proyecto + ".pkl")
    if os.path.exists(ruta):
        os.remove(ruta)