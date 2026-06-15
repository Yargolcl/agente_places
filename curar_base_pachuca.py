import pandas as pd

archivo_sucio = "Abarrotes y Miscelaneas en Pachuca, Hgo.csv"

print("--- CURANDO BASE DE DATOS INDUSTRIAL DE PACHUCA ---")

# 1. Leemos el archivo diciéndole a Python que NO tiene encabezados
df = pd.read_csv(archivo_sucio, header=None)

# 2. Recortamos y nos quedamos solo con las primeras 10 columnas útiles (adiós columnas fantasma)
df_limpio = df.iloc[:, :10]

# 3. Le inyectamos los nombres de columna EXACTOS que espera tu agente_places.py
df_limpio.columns = [
    'Razon_Social', 'Direccion', 'Colonia', 'CP',
    'Municipio', 'Estado', 'Telefono_Original', 'Email',
    'Giro', 'Tamano'
]

# 4. Exportamos la base de oro lista para el robot
archivo_salida = "Abarrotes_Pachuca_Listo.csv"
df_limpio.to_csv(archivo_salida, index=False, encoding='utf-8')

print(f"¡Base de datos curada con éxito, compa!")
print(f"Se generó '{archivo_salida}' con {len(df_limpio)} registros limpios y listos para meter al agente.")