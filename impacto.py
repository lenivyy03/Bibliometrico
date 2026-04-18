import pandas as pd

# Funcion que calcula el promedio de citas anual de cada publicacion
def calcular_promedio_citas_anual(df, año_actual=None):
    # Si no se pasa un año, toma el mas reciente del DataFrame
    if año_actual is None:
        año_actual = df['Year'].max()

    # Rellena los valores nulos en 'Cited by' con 0
    df['Cited by'] = df['Cited by'].fillna(0)

    # Calcula los años de antiguedad, suma 1 para evitar division por cero
    df['Antiguedad'] = año_actual - df['Year'] + 1

    # Divide las citas totales entre la antiguedad para obtener el promedio anual
    df['Promedio_Citas_Anual'] = df['Cited by'] / df['Antiguedad']

    # Redondea el resultado a 2 decimales
    df['Promedio_Citas_Anual'] = df['Promedio_Citas_Anual'].round(2)

    return df

# Funcion que ordena las publicaciones por promedio de citas anual
def ordenar_por_promedio_citas(df):
    # Verifica si la columna ya existe, si no la calcula
    if 'Promedio_Citas_Anual' not in df.columns:
        df = calcular_promedio_citas_anual(df)

    # Ordena de mayor a menor impacto sostenido
    df_ordenado = df.sort_values(by='Promedio_Citas_Anual', ascending=False)

    # Selecciona solo el Titulo, Año y el Promedio
    columnas_vista = ['Title', 'Year', 'Promedio_Citas_Anual']

    return df_ordenado[columnas_vista]
