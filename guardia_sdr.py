import os
import csv
import requests
import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from herramienta_whatsapp import enviar_mensaje_whatsapp, enviar_pdf_whatsapp
from dotenv import load_dotenv  # <--- AGREGA ESTA LÍNEA

load_dotenv()

# 1. Credenciales

idInstance = os.getenv("GREENAPI_ID_INSTANCE")                 # <--- CAMBIA ESTA LÍNEA
apiTokenInstance = os.getenv("GREENAPI_API_TOKEN_INSTANCE") # <--- CAMBIA ESTA LÍNEA

url_recibir = f"https://api.green-api.com/waInstance{idInstance}/receiveNotification/{apiTokenInstance}"
url_borrar = f"https://api.green-api.com/waInstance{idInstance}/deleteNotification/{apiTokenInstance}/"
archivo_bd = "2_Pipeline_SDR.csv"

# 2. El Cerebro (Filtro de Intención)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
prompt_clasificador = ChatPromptTemplate.from_messages([
    ("system", """Eres el filtro de entrada de Imphuls. Clasifica la intención del prospecto en una sola palabra:
    - POSITIVO (saluda, dice 'sí', 'dígame', o muestra apertura).
    - NEGATIVO (dice 'no', 'equivocado', 'no interesa').
    - NEUTRAL (preguntas logísticas, respuestas confusas o sin sentido para el negocio)."""),
    ("human", "Mensaje del prospecto: {mensaje}")
])
cadena_clasificadora = prompt_clasificador | llm


# --- NUEVOS SUPERPODERES (Manejo del Excel) ---

def limpiar_numero(telefono_bruto):
    """Limpia el número del Excel para compararlo con el que entra de Green API"""
    numeros_solo = ''.join(filter(str.isdigit, str(telefono_bruto)))
    if numeros_solo.startswith("52") and len(numeros_solo) > 10:
        numeros_solo = numeros_solo[2:]
    if len(numeros_solo) == 10:
        return f"521{numeros_solo}"
    return numeros_solo


def buscar_y_actualizar_empresa(numero_entrante, nuevo_estatus=None):
    """Busca quién nos escribió y actualiza su estatus blindando el Excel contra errores"""
    empresa_encontrada = None
    filas_actualizadas = []
    encontrado = False
    estatus_actual = None

    try:
        # Leemos la base de datos
        with open(archivo_bd, mode='r', encoding='utf-8-sig') as archivo:
            lector = csv.DictReader(archivo)

            # PROTECCIÓN 1: Limpiar espacios ocultos en los encabezados
            nombres_columnas = [str(col).strip() for col in lector.fieldnames] if lector.fieldnames else []

            # PROTECCIÓN 2: Asegurar que exista la columna Estatus
            if "Estatus" not in nombres_columnas:
                nombres_columnas.append("Estatus")

            for fila_bruta in lector:
                # Limpiamos todos los espacios basura de los datos y las llaves
                fila = {str(k).strip(): str(v).strip() if v else "" for k, v in fila_bruta.items()}

                # Aseguramos que la fila tenga su llave
                if "Estatus" not in fila:
                    fila["Estatus"] = ""

                num_excel = limpiar_numero(fila.get("Telefono_Google", ""))

                if num_excel == numero_entrante:
                    empresa_encontrada = fila.get("Razon_Social", "su empresa")
                    estatus_actual = fila.get("Estatus", "")
                    encontrado = True

                    if nuevo_estatus:
                        fila["Estatus"] = nuevo_estatus

                filas_actualizadas.append(fila)

        # Si pedimos actualizar, reescribimos con cuidado
        if encontrado and nuevo_estatus:
            with open(archivo_bd, mode='w', newline='', encoding='utf-8-sig') as archivo:
                escritor = csv.DictWriter(archivo, fieldnames=nombres_columnas)
                escritor.writeheader()
                escritor.writerows(filas_actualizadas)

        return empresa_encontrada, estatus_actual

    except FileNotFoundError:
        print("⚠️ No se encontró la base de datos CSV.")
        return None, None
    except Exception as e:
        print(f"⚠️ Error interno procesando el Excel: {e}")
        return None, None


# --- EL MOTOR PRINCIPAL ---

def guardia_autonomo():
    print("🛡️ Guardia SDR Activado. Escuchando respuestas de prospectos...")

    while True:
        try:
            respuesta = requests.get(url_recibir)

            if respuesta.status_code == 200 and respuesta.json():
                datos = respuesta.json()
                receipt_id = datos.get('receiptId')
                body = datos.get('body', {})

                if body.get('typeWebhook') == 'incomingMessageReceived' and body.get('messageData', {}).get(
                        'typeMessage') == 'textMessage':
                    texto_recibido = body['messageData']['textMessageData']['textMessage']
                    numero_remitente = body['senderData']['sender'].split('@')[0]

                    print(f"\n📩 Mensaje recibido de {numero_remitente}: '{texto_recibido}'")

                    # 1. Consultamos el Cerebro Compartido (Excel)
                    razon_social, estatus = buscar_y_actualizar_empresa(numero_remitente)

                    if not razon_social:
                        print("⚠️ Este número no está en nuestra Base de Datos. Ignorando...")

                    # EL ARREGLO ESTÁ AQUÍ: Solo detenemos al bot si YA se envió el PDF.
                    elif estatus == "PDF Enviado":
                        print(
                            f"📌 {razon_social} ya tiene el documento. El bot se detiene para que Luis Carlos/Amparo cierren la cita.")

                    else:
                        print(f"🏢 Empresa identificada: {razon_social}. Evaluando intención...")

                        # 2. La IA analiza
                        intencion = cadena_clasificadora.invoke({"mensaje": texto_recibido}).content.strip().upper()
                        print(f"🎯 Intención detectada: {intencion}")

                        # 3. La Acción y Máquina de Estados
                        if "POSITIVO" in intencion:

                            # ESTADO 1: Es el primer "Sí" al rompehielos
                            if estatus == "" or estatus is None:
                                print(f"🚀 Primer contacto exitoso. Disparando Pitch Corporativo a {razon_social}...")
                                pitch = f"Hola, me comunico a la Dirección de Operaciones de {razon_social}. Soy Luis Carlos de la firma Imphuls. Hemos trabajado con empresas como Cargill y Alsea ayudándolas a optimizar su operación mediante un diagnóstico sistémico basado en metodologías ExO. ¿Es este el canal correcto para compartirles nuestro PDF ejecutivo sobre 'Arquitectura Organizacional'?"
                                enviar_mensaje_whatsapp(numero_remitente, pitch)
                                buscar_y_actualizar_empresa(numero_remitente, nuevo_estatus="Pitch Enviado")
                                print("✅ Base de datos actualizada a 'Pitch Enviado'.")

                            # ESTADO 2: Ya le habíamos mandado el Pitch, ahora mandamos el PDF
                            elif estatus == "Pitch Enviado":
                                print(f"🎯 El prospecto de {razon_social} aceptó el documento. Disparando PDF...")

                                # Acomoda tu PDF en la misma carpeta y pon el nombre exacto aquí:
                                nombre_pdf_local = "Organizaciones_inteligentes.pdf"

                                # Un texto cortito que se manda pegado al PDF
                                texto_adjunto = "Aquí tiene el documento ejecutivo. Quedo atento a sus comentarios para agendar nuestra sesión de 15 minutos."

                                enviar_pdf_whatsapp(numero_remitente, nombre_pdf_local,
                                                    nombre_documento="Arquitectura_Organizacional_Imphuls.pdf",
                                                    mensaje_adjunto=texto_adjunto)

                                buscar_y_actualizar_empresa(numero_remitente, nuevo_estatus="PDF Enviado")
                                print("✅ Base de datos actualizada a 'PDF Enviado'.")

                        elif "NEGATIVO" in intencion:
                            print(f"🛑 {razon_social} declinó. Actualizando base de datos.")
                            buscar_y_actualizar_empresa(numero_remitente, nuevo_estatus="Rechazado")

                        else:
                            print("⚖️ Mensaje neutral. Esperando intervención manual.")

                # Borramos la notificación
                requests.delete(f"{url_borrar}{receipt_id}")

            time.sleep(3)

        except Exception as e:
            print(f"⚠️ Error de red: {e}")
            time.sleep(5)


if __name__ == "__main__":
    guardia_autonomo()