import os
import time
from dotenv import load_dotenv
import pandas as pd
import requests

# ==========================================
# ACTIVAR VARIABLES DE ENTORNO
# ==========================================
ruta_carpeta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_archivo_env = os.path.join(ruta_carpeta_actual, '.env')
load_dotenv(dotenv_path=ruta_archivo_env)

# ==========================================
# CONFIGURACIÓN DEL EXPLORADOR MAESTRO
# ==========================================
API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')
OUTPUT_PATH = 'Z_Archivo_Pruebas/Nuevos_Miscelaneas_BarriosAltos_Pachuca.csv'

# 🎯 EL CAMBIO ESTRATÉGICO: Para barrios altos icónicos desactivamos el filtro (None)
# porque Google los registra bajo el CP 42000 o sin CP. Sus nombres ya son el filtro definitivo.
FILTRO_CP = None

PLACES_URL = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
DETAILS_URL = 'https://maps.googleapis.com/maps/api/place/details/json'


# ==========================================
# MOTOR HÍBRIDO DE EXPLORACIÓN TOTAL
# ==========================================
def barrido_total_pachuca(giro, zonas, ciudad="Pachuca, Hidalgo"):
    print("=======================================================")
    print(f"🚀 INICIANDO RADAR HÍBRIDO INDUSTRIAL: [{giro.upper()}]")
    print(f"🎯 FILTRO INTEGRADO DE C.P.: [{FILTRO_CP if FILTRO_CP else 'DESACTIVADO (MODO LIBRE PARA BARRIOS)'}]")
    print("=======================================================")

    dict_lugares_unicos = {}
    session = requests.Session()

    # -------------------------------------------------------
    # FASE A: BARRIDO MULTI-ZONA CON PAGINACIÓN BLINDADA
    # -------------------------------------------------------
    for i, zona in enumerate(zonas):
        query_especifica = f"{giro} {zona} {ciudad}"
        print(f"\n📡 [{i + 1}/{len(zonas)}] Escaneando sector: [{query_especifica}]")

        params = {
            'query': query_especifica,
            'key': API_KEY,
            'language': 'es'
        }

        pagina_sector = 1

        while True:
            try:
                response = session.get(PLACES_URL, params=params)
                data = response.json()
                status = data.get('status')

                if status == 'OK':
                    resultados_hoja = data.get('results', [])
                    nuevos_validos = 0
                    descartados_cp = 0

                    for place in resultados_hoja:
                        p_id = place.get('place_id')
                        direccion = place.get('formatted_address', '')

                        # FILTRO DE PROTECCIÓN GEOGRÁFICA (Solo actúa si no es None)
                        if FILTRO_CP and (FILTRO_CP not in direccion):
                            descartados_cp += 1
                            continue

                        if p_id not in dict_lugares_unicos:
                            dict_lugares_unicos[p_id] = place
                            nuevos_validos += 1

                    print(
                        f"   [Pág {pagina_sector}] -> Guardados en este pase: {nuevos_validos} | Fuera de C.P.: {descartados_cp}")

                    # CONTROL DE PAGINACIÓN INTERNA
                    next_page_token = data.get('next_page_token')
                    if next_page_token:
                        pagina_sector += 1
                        print("   ⏳ Siguiente página detectada. Calentando token (Pausa de 4 segundos)...")
                        time.sleep(4)

                        params = {
                            'pagetoken': next_page_token,
                            'key': API_KEY
                        }
                    else:
                        break

                elif status == 'INVALID_REQUEST' and 'pagetoken' in params:
                    print("   ❌ Token bloqueado o expirado por Google. Saltando de sector de forma segura.")
                    break
                else:
                    print(f"   ⚠️ Fin del sector o aviso de Google: {status}")
                    break

            except Exception as e:
                print(f"   ❌ Error en la ráfaga del sector: {e}")
                break

    # -------------------------------------------------------
    # FASE B: ENRIQUECIMIENTO PROFUNDO (EXTRACCIÓN QUIRÚRGICA)
    # -------------------------------------------------------
    total_encontrados = len(dict_lugares_unicos)
    if total_encontrados == 0:
        print(f"\n⚠️ El radar terminó. Ningún local coincidió con los criterios.")
        return

    print(f"\n🧠 Barrido terminado. Total NETO de locales únicos descubiertos: {total_encontrados}")
    print("Iniciando Fase de Enriquecimiento (Extrayendo teléfonos y sitios web)...")

    resultados_totales = []

    for index, (place_id, place) in enumerate(dict_lugares_unicos.items()):
        nombre = place.get('name', 'Sin Nombre')
        direccion = place.get('formatted_address', 'Sin Dirección')

        print(f"[{index + 1}/{total_encontrados}] Extrayendo datos de: {nombre}")

        det_params = {'place_id': place_id, 'fields': 'website,formatted_phone_number', 'key': API_KEY}
        website = 'Sin Web'
        telefono = 'Sin Teléfono'

        try:
            det_response = session.get(DETAILS_URL, params=det_params, timeout=10).json()
            if det_response.get('status') == 'OK':
                result = det_response.get('result', {})
                website = result.get('website', 'Sin Web')
                telefono = result.get('formatted_phone_number', 'Sin Teléfono')
        except Exception as e:
            print(f"    ⚠️ Error en detalles de {nombre}: {e}")
            website = 'Error Details'
            telefono = 'Error Details'

        resultados_totales.append({
            'Razon_Social': nombre,
            'Direccion': direccion,
            'Telefono_Google': telefono,
            'Website_Google': website,
            'Status_Negocio': place.get('business_status', 'N/A'),
            'Estrellas': place.get('rating', 0)
        })
        time.sleep(0.2)

    # -------------------------------------------------------
    # FASE C: EXPORTACIÓN DE LA BASE DE ORO
    # -------------------------------------------------------
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df = pd.DataFrame(resultados_totales)
    df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8')

    print("\n=======================================================")
    print(f"🎉 ¡SISTEMA CALIBRADO CON ÉXITO COMPA!")
    print(f"Se consolidaron {len(resultados_totales)} prospectos reales de los Barrios Altos.")
    print(f"Tu archivo final indestructible está listo en: {OUTPUT_PATH}")
    print("=======================================================")


if __name__ == "__main__":
    # Giro comercial en bruto
    giro_commercial = "Miscelaneas"

    # Lista quirúrgica de tus barrios tradicionales
    barrios_altos = [
        "La alcantarilla",
        "el arbolito",
        "el atorón",
        "La palma",
        "San Juan pachuca",
    ]

    barrido_total_pachuca(giro_commercial, barrios_altos)