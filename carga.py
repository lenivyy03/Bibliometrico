import pandas as pd
from pandas.errors import EmptyDataError


# Función para cargar un CSV y validar su estructura básica
def cargar_csv(ruta):
    try:
        # Intentamos leer con encodings comunes en archivos exportados
        ultimo_error = None
        for encoding in ("utf-8-sig", "utf-8", "latin1", "cp1252"):
            try:
                df = pd.read_csv(ruta, encoding=encoding)
                break
            except UnicodeDecodeError as e:
                ultimo_error = e
        else:
            raise ultimo_error

        # Limpiamos espacios en nombres de columnas
        df.columns = df.columns.str.strip()

        columnas_criticas = ["Authors", "Title", "Year", "Cited by", "Affiliations"]
        columnas_apa = ["Source title", "Volume", "Issue", "DOI"]
        columnas_opcionales = ["Page start", "Page end", "Art. No."]

        faltantes_criticas = [c for c in columnas_criticas if c not in df.columns]
        faltantes_apa = [c for c in columnas_apa if c not in df.columns]
        faltantes_opcionales = [c for c in columnas_opcionales if c not in df.columns]

        archivo_vacio = df.empty
        ok = len(faltantes_criticas) == 0 and not archivo_vacio

        return {
            "ok": ok,
            "dataframe": df,
            "total_registros": len(df),
            "faltantes_criticas": faltantes_criticas,
            "faltantes_apa": faltantes_apa,
            "faltantes_opcionales": faltantes_opcionales,
            "archivo_vacio": archivo_vacio,
            "mensaje": "Archivo cargado correctamente" if ok else "El archivo está vacío o no cumple con las columnas críticas requeridas",
            "preview": df.head().to_dict(orient="records")
        }

    except FileNotFoundError:
        return {"ok": False, "error": "El archivo no existe"}
    except EmptyDataError:
        return {"ok": False, "error": "El archivo está vacío"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


