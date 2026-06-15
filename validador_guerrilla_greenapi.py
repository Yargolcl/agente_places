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
# CONFIGURACIÓN DE APIS Y ARCHIVOS
# ==========================================
# Jalamos tus credenciales de GreenAPI desde el mismo .env
ID_INSTANCE = os.getenv('GREEN_API_ID_INSTANCE')
API_TOKEN_INSTANCE = os.getenv('GREEN_API_TOKEN_INSTANCE')

# Archivos de entrada y salida (Ajusta el archivo de entrada según el script que uses antes)
FILE_PATH = 'Z_Archivo_Pruebas/Base_Validada_Abarrotes_Pachuca.csv'
OUTPUT_PATH = 'Z_Archivo_Pruebas/Base_Final_Oro_Puro.csv'


# ==========================================
# FUNCIONES DE FORMATEO
# ==========================================
def formatear_mexico(tel):
    """Limpia el teléfono y lo deja en el formato internacional rígido que exige GreenAPI."""
    num = re.sub(r'\D', '', str(tel))
    if len(num) == 10:
        return f"52{num}"
    if len(num) == 12 and num.startswith('52'):
        return num
    return None


# ==========================================
# MOTOR PRINCIPAL
# ==========================================
def main():
    print("=======================================================")
    print("🚀 INICIANDO VALIDADOR GUERRILLA CON GREENAPI (ExO Speed)")
    print("=======================================================")

    # Validamos que existan las llaves de GreenAPI en memoria
    if not ID_INSTANCE or not API_TOKEN_INSTANCE:
        print("❌ Error Crítico: Falta configurar las variables de GreenAPI en tu .env")
        print("Asegúrate de tener GREEN_API_ID_INSTANCE y GREEN_API_TOKEN_INSTANCE")
        return

    # 1. Cargar la base de datos
    if not os.path.exists(FILE_PATH):
        print(f"❌ No encontré el archivo de entrada en: {FILE_PATH}")
        return

    df = pd.read_csv(FILE_PATH, encoding='utf-8')
    resultados = []

    # Endpoint oficial de GreenAPI para checar la existencia de WhatsApp
    url_green = f"https://api.green-api.com/waInstance{ID_INSTANCE}/checkPhone/{API_TOKEN_INSTANCE}"
    headers = {'Content-Type': 'application/json'}

    print(f"Preparado para validar {len(df)} registros. Conectando con GreenAPI...")

    # 2. Procesar ráfaga de peticiones
    for index, row in df.iterrows():
        # Primero intentamos jalar el Teléfono de Google, si no hay, el Original
        tel_raw = row.get('Telefono_Google', row.get('Telefono', ''))
        numero = formatear_mexico(tel_raw)

        if not numero:
            print(f"[{index + 1}/{len(df)}] ⚠️ {row['Razon_Social']} -> Formato de Teléfono Incorrecto.")
            resultados.append("Formato Incorrecto")
            continue

        print(f"[{index + 1}/{len(df)}] Verificando en la red: {numero} ({row['Razon_Social']})...", end="")

        payload = {"phoneNumber": int(numero)}

        try:
            # Lanzamos la petición directa al servidor de GreenAPI
            response = requests.post(url_green, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                # GreenAPI responde estrictamente: {"existsWhatsapp": true/false}
                existe = data.get('existsWhatsapp', False)

                if existe:
                    print(" 🔥 [SI]")
                    resultados.append("SI")
                else:
                    print(" ❌ [NO]")
                    resultados.append("NO")
            else:
                print(f" ⚠️ [Error Servidor: {response.status_code}]")
                resultados.append("Error API")

        except Exception as e:
            print(f" ⚠️ [Error de Conexión: {str(e)[:30]}]")
            resultados.append("Error Conexión")

        # Pausa táctica milimétrica solo para no saturar ráfagas, pero va volando
        time.sleep(0.2)

    # 3. Ensamblar la columna de Oro Puro
    df['WhatsApp_Validado'] = resultados

    # 4. Exportar el archivo final limpio
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8')

    print("\n=======================================================")
    print(f"🎉 ¡PROCESO TERMINADO COMPA!")
    print(f"Tu Base Final de Oro Puro está lista en: {OUTPUT_PATH}")
    print(f"Total Registros Listos para Amparo: {len(df[df['WhatsApp_Validado'] == 'SI'])}")
    print("=======================================================")


if __name__ == "__main__":
    main()