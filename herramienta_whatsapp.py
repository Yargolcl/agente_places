import os
from dotenv import load_dotenv
import requests

load_dotenv()

# Tus Credenciales de Green API
GREENAPI_ID_INSTANCE = os.getenv("GREENAPI_ID_INSTANCE")
GREENAPI_API_TOKEN_INSTANCE = os.getenv("GREENAPI_API_TOKEN_INSTANCE")


def enviar_mensaje_whatsapp(numero_destino, mensaje):
    """El brazo original para enviar texto puro."""
    url = f"https://api.green-api.com/waInstance{GREENAPI_ID_INSTANCE}/sendMessage/{GREENAPI_API_TOKEN_INSTANCE}"
    payload = {
        "chatId": f"{numero_destino}@c.us",
        "message": mensaje
    }
    headers = {'Content-Type': 'application/json'}

    try:
        respuesta = requests.post(url, json=payload, headers=headers)
        print(f"📡 Disparando texto a {numero_destino}...")
        if respuesta.status_code == 200:
            return respuesta.json()
        else:
            print(f"❌ Error al enviar. {respuesta.text}")
            return None
    except Exception as e:
        print(f"⚠️ Error de red: {e}")
        return None


def enviar_pdf_whatsapp(numero_destino, ruta_archivo, nombre_documento="Documento.pdf", mensaje_adjunto=""):
    """El NUEVO brazo pesado para disparar archivos locales."""
    url = f"https://api.green-api.com/waInstance{GREENAPI_ID_INSTANCE}/sendFileByUpload/{GREENAPI_API_TOKEN_INSTANCE}"

    # Preparamos los datos del destinatario y el texto que acompaña al archivo
    payload = {
        'chatId': f"{numero_destino}@c.us",
        'fileName': nombre_documento,
        'caption': mensaje_adjunto
    }

    try:
        # Abrimos el archivo de tu Mac en modo binario ('rb')
        with open(ruta_archivo, 'rb') as archivo:
            # Empaquetamos el archivo para enviarlo por internet
            files = [
                ('file', (nombre_documento, archivo, 'application/pdf'))
            ]

            print(f"📎 Subiendo y disparando PDF a {numero_destino}...")
            respuesta = requests.post(url, data=payload, files=files)

            if respuesta.status_code == 200:
                print("✅ ¡Impacto confirmado! PDF entregado.")
                return respuesta.json()
            else:
                print(f"❌ Error al enviar PDF: {respuesta.text}")
                return None

    except FileNotFoundError:
        print(f"⚠️ ¡Alerta! El Agente no encontró el archivo: {ruta_archivo}")
        print("Asegúrate de que esté en la misma carpeta y se llame exactamente igual.")
        return None
    except Exception as e:
        print(f"⚠️ Error al subir el archivo: {e}")
        return None