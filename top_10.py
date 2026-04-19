# Esta función devuelve los datos suficientes para las HU 45, 46 y 48 (visualizar en otra función)
def top_10_trabajos(df):
	# Hacemos una copia del dataframe
    	copia = df.copy()
	# Convertimos los valores a numeros
    	copia["Cited by"] = pd.to_numeric(copia["Cited by"], errors="coerce").fillna(0)
	
	top_10 = copia.sort_values(by=["Cited by"], ascending=False).head(10)
	lista_top10 = []

	for index, row in top_10.iterrows():
		referencia = construir_referencia_apa(row)
        	citas = int(row["Cited by"])
		year = row['Year']
		DOI = row['DOI']
		lista_top10.append([referencia,citas,year,DOI])

	return lista_top10
