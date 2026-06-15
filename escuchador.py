import os
from dotenv import load_dotenv
import requests
import time

load_dotenv()

# 1. Tus Credenciales
GREENAPI_ID_INSTANCE = os.getenv("GREENAPI_ID_INSTANCE")
GREENAPI_API_TOKEN_INSTANCE = os.getenv("GREENAPI_API_TOKEN_INSTANCE")

url_recibir = f"https://api.green-api.com/waInstance{GREENAPI_ID_INSTANCE}/receiveNotification/{GREENAPI_API_TOKEN_INSTANCE}"
url_borrar = f"https://api.green-api.com/waInstance{GREENAPI_ID_INSTANCE}/deleteNotification/{GREENAPI_API_TOKEN_INSTANCE}/"


def escuchar_whatsapp():
    print("🎧 Oídos activados (Modo Rayos X). Esperando actividad...")

    while True:
        try:
            respuesta = requests.get(url_recibir)

            if respuesta.status_code == 200 and respuesta.json():
                datos = respuesta.json()
                receipt_id = datos.get('receiptId')
                body = datos.get('body', {})
                tipo_notificacion = body.get('typeWebhook', 'Desconocido')

                print("\n" + "=" * 50)
                print(f"🚨 ALERTA: El servidor detectó actividad de tipo: {tipo_notificacion}")
                print(f"📦 DATOS CRUDOS: {body}")
                print("=" * 50 + "\n")

                # Borramos la notificación para que pueda leer la siguiente
                requests.delete(f"{url_borrar}{receipt_id}")

            time.sleep(3)

        except Exception as e:
            print(f"⚠️ Error de conexión: {e}")
            time.sleep(5)


if __name__ == "__main__":
    escuchar_whatsapp()