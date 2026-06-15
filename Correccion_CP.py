import pandas as pd
import os

# 1. Definimos el nombre exacto del archivo en la misma carpeta del script
archivo_falso_excel = "CodigosPostalesTiza.xls"

# 2. Validamos si el archivo realmente está ahí para evitar errores
if not os.path.exists(archivo_falso_excel):
    print(f"❌ No encontré el archivo '{archivo_falso_excel}' en esta carpeta, compa.")
    print("Por favor, revisa que esté guardado exactamente en la misma ruta que este script de Python.")
else:
    print(f"¡Archivo localizado con éxito!: {archivo_falso_excel}")
    print("--- PROCESANDO BASE DE DATOS DE SEPOMEX ---")

    # Extraemos todas las tablas que vengan dentro del HTML oculto
    tablas = pd.read_html(archivo_falso_excel)
    print(f"Tablas detectadas internamente: {len(tablas)}")

    # EL TRUCO MAESTRO: Elegimos la tabla que tenga más renglones (así ignoramos el aviso legal)
    df_datos = max(tablas, key=len)

    print(f"¡Tabla de datos seleccionada! Contiene {df_datos.shape[0]} registros de Pachuca.")

    # 3. Creamos la carpeta de pruebas del proyecto si no existe
    os.makedirs('Z_Archivo_Pruebas', exist_ok=True)

    # Definimos la ruta de salida para tu base limpia
    ruta_salida = 'Z_Archivo_Pruebas/CP_Tiza_Limpio.csv'

    # Guardamos la data en un formato CSV real y limpio
    df_datos.to_csv(ruta_salida, index=False, encoding='utf-8')

    print("\n=======================================================")
    print(f"¡HECHO, COMPA! Estructura corregida al 100%.")
    print(f"Tu archivo limpio y listo para los agentes está en: {ruta_salida}")
    print("=======================================================")