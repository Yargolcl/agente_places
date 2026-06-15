import os
import re
import time
from dotenv import load_dotenv
import pandas as pd
import requests

# ==========================================
# ACTIVAR VARIABLES DE ENTORNO (RUTA ABSOLUTA)
# ==========================================
ruta_carpeta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_archivo_env = os.path.join(ruta_carpeta_actual, '.env')

load_dotenv(dotenv_path=ruta_archivo_env)

# ==========================================
# CONFIGURACIÓN DEL AGENTE
# ==========================================
API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')
FILE_PATH = 'Z_Archivo_Pruebas/Z_Archivo_Pruebas/Abarrotes_Pachuca_Listo.csv'
OUTPUT_PATH = 'Z_Archivo_Pruebas/Base_Validada_Abarrotes_Pachuca.csv'

# Endpoint de Google Places (Text Search)
PLACES_URL = 'https://maps.googleapis.com/maps/api/place/textsearch/json'


# ==========================================
# FUNCIONES DE LIMPIEZA
# ==========================================
def clean_name(name):
    """Limpia la Razón Social para que la búsqueda sea humana."""
    name = str(name).upper()
    name = re.sub(
        r',\s*S\.?A\.?\s*DE\s*C\.?V\.?|S\.?A\.?\s*DE\s*C\.V\.?|S\.?\s*DE\s*R\.?L\.?\s*DE\s*C\.?V\.?',
        '',
        name,
    )
    return name.strip()


# ==========================================
# MOTOR PRINCIPAL
# ==========================================
def main():
    print("Iniciando Agente Validador de Google Places...")

    print("\n--- 🕵️‍♂️ REVISIÓN DE SEGURIDAD DEL ENTORNO ---")
    print(f"1. Ruta donde el script está buscando el archivo: {ruta_archivo_env}")

    existe_archivo = os.path.exists(ruta_archivo_env)
    print(f"2. ¿El archivo .env existe físicamente ahí?: {'✅ SÍ EXISTE' if existe_archivo else '❌ NO EXISTE AHÍ'}")

    if existe_archivo:
        print("3. Leyendo llaves internas dentro del archivo...")
        try:
            with open(ruta_archivo_env, 'r', encoding='utf-8') as f:
                lineas = f.readlines()
                for i, linea in enumerate(lineas):
                    linea_limpia = linea.strip()
                    if '=' in linea_limpia:
                        llave = linea_limpia.split('=')[0].strip()
                        valor_oculto = linea_limpia.split('=')[1].strip()[:4] + "..." if len(
                            linea_limpia.split('=')) > 1 else "VACÍO"
                        print(f"   -> Encontrada variable: '{llave}' (Inicia con: {valor_oculto})")
        except Exception as e:
            print(f"   ❌ Error al intentar abrir el archivo: {e}")

    print(f"4. API Key cargada en memoria por Python: {API_KEY}")
    print("-------------------------------------------\n")

    if not API_KEY:
        print("❌ Error Crítico: No se detectó la GOOGLE_PLACES_API_KEY en tu archivo .env.")
        return

    # 1. Cargar la base de datos curada
    df = pd.read_csv(FILE_PATH, encoding='utf-8')

    # Listas para guardar la data enriquecida (Se agrega la lista de nombres)
    nombres_google = []  # <--- NUEVA LÍNEA: Para almacenar el nombre real de Google
    websites = []
    telefonos_reales = []
    status = []
    ratings = []

    # 2. Procesar fila por fila
    for index, row in df.iterrows():
        nombre_raw = str(row['Razon_Social']).strip().upper()
        direccion = str(row['Direccion']).strip()

        # EL FILTRO INTELIGENTE
        if nombre_raw in ['', 'NAN', 'MISCELÁNEA', 'MISCELANEA', 'ABARROTES', 'SIN NOMBRE', 'TIENDA', 'PERSONA FÍSICA',
                          'PERSONA FISICA', 'NO PROPORCIONO']:
            giro_comoditizado = "MISCELANEA ABARROTES"
        else:
            giro_comoditizado = clean_name(row['Razon_Social'])

        query = f"{giro_comoditizado} {direccion} Pachuca"
        print(f"[{index + 1}/{len(df)}] Buscando en Places: [{query}]")

        params = {'query': query, 'key': API_KEY}

        try:
            response = requests.get(PLACES_URL, params=params)
            data = response.json()

            if data['status'] == 'OK' and len(data['results']) > 0:
                best_match = data['results'][0]

                # EXTRAEMOS EL NOMBRE ACTUALIZADO QUE TIENE GOOGLE MAPS
                nombres_google.append(best_match.get('name', 'N/A'))  # <--- NUEVA LÍNEA

                place_id = best_match.get('place_id', 'N/A')
                status.append(best_match.get('business_status', 'DESCONOCIDO'))
                ratings.append(best_match.get('rating', 0))

                # Petición de Detalles para Website y Teléfono
                details_url = 'https://maps.googleapis.com/maps/api/place/details/json'
                det_params = {'place_id': place_id, 'fields': 'website,formatted_phone_number', 'key': API_KEY}
                det_response = requests.get(details_url, params=det_params).json()

                if det_response['status'] == 'OK':
                    websites.append(det_response['result'].get('website', 'Sin Web'))
                    telefonos_reales.append(det_response['result'].get('formatted_phone_number', 'Sin Teléfono'))
                else:
                    websites.append('Sin Web')
                    telefonos_reales.append('Sin Teléfono')
            else:
                nombres_google.append('No Encontrado')  # <--- NUEVA LÍNEA
                websites.append('No Encontrado')
                telefonos_reales.append('No Encontrado')
                status.append('N/A')
                ratings.append('N/A')

        except Exception as e:
            print(f"Error procesando {giro_comoditizado}: {e}")
            nombres_google.append('Error')  # <--- NUEVA LÍNEA
            websites.append('Error')
            telefonos_reales.append('Error')
            status.append('Error')
            ratings.append('Error')

        time.sleep(0.5)

    # 3. Ensamblar los resultados en la base de datos original
    df['Nombre_Google'] = nombres_google  # <--- NUEVA LÍNEA: Se inyecta la columna esperada
    df['Website_Google'] = websites
    df['Telefono_Google'] = telefonos_reales
    df['Status_Negocio'] = status
    df['Estrellas'] = ratings

    # 4. Guardar la nueva base de oro limpia (Se removió el bloque duplicado viejo)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8')
    print(f"\n=======================================================")
    print(f"¡OPERACIÓN EXITOSA COMPA!")
    print(f"Base de datos rejuvenecida y guardada en: {OUTPUT_PATH}")
    print(f"=======================================================")


if __name__ == "__main__":
    main()