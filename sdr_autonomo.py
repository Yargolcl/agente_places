import os
from dotenv import load_dotenv
import requests
import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from herramienta_whatsapp import enviar_mensaje_whatsapp

# 1. Tus Credenciales

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GREENAPI_ID_INSTANCE = os.getenv("GREENAPI_ID_INSTANCE")
GREENAPI_API_TOKEN_INSTANCE = os.getenv("GREENAPI_API_TOKEN_INSTANCE")

url_recibir = f"https://api.green-api.com/waInstance{GREENAPI_ID_INSTANCE}/receiveNotification/{GREENAPI_API_TOKEN_INSTANCE}"
url_borrar = f"https://api.green-api.com/waInstance{GREENAPI_ID_INSTANCE}/deleteNotification/{GREENAPI_API_TOKEN_INSTANCE}/"

# 2. El Cerebro (Baja temperatura para que sea analítico y no invente cosas)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, api_key=OPENAI_API_KEY)

# Le enseñamos a LangChain a ser un "Filtro" de respuestas
prompt_clasificador = ChatPromptTemplate.from_messages([
    ("system", """Eres el filtro de entrada de la firma Imphuls. Tu trabajo es leer la respuesta de un prospecto de negocios y clasificar su intención en una sola palabra.
    Reglas estrictas, responde ÚNICAMENTE con una de estas opciones:
    - POSITIVO (Si saluda de vuelta, dice 'sí', 'dígame', 'hola buen día', o muestra apertura).
    - NEGATIVO (Si dice 'no', 'equivocado', 'no me interesa', 'deje de molestar').
    - NEUTRAL (Si hace una pregunta que no puedes responder o manda algo sin sentido)."""),
    ("human", "Mensaje del prospecto: {mensaje_cliente}")
])

cadena_clasificadora = prompt_clasificador | llm


def escuchar_y_responder():
    print("🤖 Agente SDR Autónomo Activado. Monitoreando respuestas en tiempo real...")

    while True:
        try:
            respuesta = requests.get(url_recibir)

            if respuesta.status_code == 200 and respuesta.json():
                datos = respuesta.json()
                receipt_id = datos.get('receiptId')
                body = datos.get('body', {})

                if body.get('typeWebhook') == 'incomingMessageReceived':
                    mensaje_data = body.get('messageData', {})
                    remitente_id = body.get('senderData', {}).get('sender', '')
                    nombre_remitente = body.get('senderData', {}).get('senderName', 'su empresa')

                    if mensaje_data.get('typeMessage') == 'textMessage':
                        texto_recibido = mensaje_data.get('textMessageData', {}).get('textMessage', '')
                        numero_limpio = remitente_id.split('@')[0]

                        print(f"\n📩 Mensaje de {nombre_remitente}: '{texto_recibido}'")
                        print("🧠 Procesando intención con LangChain...")

                        # 3. La IA analiza el mensaje
                        analisis = cadena_clasificadora.invoke({"mensaje_cliente": texto_recibido})
                        intencion = analisis.content.strip().upper()

                        print(f"🎯 Diagnóstico de la IA: {intencion}")

                        # 4. El Árbol de Decisiones
                        if "POSITIVO" in intencion:
                            print("🚀 ¡Luz verde! Disparando Pitch Corporativo...")

                            pitch = f"Hola, me comunico a la Dirección de Operaciones de {nombre_remitente}. Soy Luis Carlos de la firma Imphuls. Hemos trabajado con empresas como Cargill y Alsea ayudándolas a optimizar su operación mediante un diagnóstico sistémico basado en metodologías ExO. ¿Es este el canal correcto para compartirles nuestro PDF ejecutivo sobre 'Arquitectura Organizacional'?"

                            enviar_mensaje_whatsapp(numero_limpio, pitch)
                            print("✅ Pitch enviado exitosamente.")

                        elif "NEGATIVO" in intencion:
                            print("🛑 El prospecto no tiene interés. Descartando sin enviar nada.")

                        else:
                            print("⚠️ Respuesta neutral o confusa. Requiere revisión humana por Amparo.")

                # CRÍTICO: Borramos la notificación para no atorarnos
                requests.delete(f"{url_borrar}{receipt_id}")

            time.sleep(3)

        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    escuchar_y_responder()