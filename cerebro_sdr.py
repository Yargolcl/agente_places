import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv  # <--- AGREGA ESTA LÍNEA

load_dotenv()             # <--- AGREGA ESTA LÍNEA
# Importamos el "brazo" que construimos en el paso anterior
# (Asegúrate de que herramienta_whatsapp.py esté en la misma carpeta)
from herramienta_whatsapp import enviar_mensaje_whatsapp

# 1. Ponemos la llave del cerebro (Tu API Key de OpenAI)


# 2. Inicializamos el modelo (El Motor Cognitivo)
# Usamos gpt-4o-mini porque es rapidísimo, muy económico a escala y brillante para B2B
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 3. Construimos la "Personalidad" (System Prompt)
# Aquí inyectamos tu propiedad intelectual y autoridad.
prompt = ChatPromptTemplate.from_messages([
    ("system", """Eres un SDR (Representante de Desarrollo de Ventas) de nivel ejecutivo trabajando para Imphuls, una firma de consultoría con 30 años de prestigio.
    Tu objetivo es escribir un mensaje de WhatsApp rompehielos (máximo 4 renglones) para un Director de Planta o de Operaciones.
    El tono debe ser: Autoridad, directo, corporativo pero conversacional (no parezcas un robot, no uses emojis excesivos).
    El gancho: Mencionar que tenemos un diagnóstico sistémico basado en metodologías ExO (Organizaciones Exponenciales) que ha ayudado a empresas como Cargill y Alsea a reducir cuellos de botella y rotación.
    Llamado a la acción: Preguntar de forma casual si este es el canal correcto para compartirle nuestro PDF ejecutivo de 2 hojas sobre 'Arquitectura Organizacional'."""),
    ("human",
     "Redacta el mensaje hiper-personalizado para el Director de Operaciones de la empresa: {empresa_objetivo}.")
])

# 4. Conectamos la Personalidad con el Cerebro (La Cadena de LangChain)
cadena = prompt | llm


def prospectar_empresa(nombre_empresa, numero_telefono):
    print(f"🧠 Analizando el perfil y redactando estrategia para {nombre_empresa}...")

    # El cerebro redacta el mensaje en milisegundos
    respuesta = cadena.invoke({"empresa_objetivo": nombre_empresa})
    mensaje_redactado = respuesta.content

    print("\n📝 Mensaje redactado por la Inteligencia Artificial:")
    print("-" * 50)
    print(mensaje_redactado)
    print("-" * 50)

    # 5. El cerebro le da la orden al "Brazo" de WhatsApp
    print(f"\n🚀 Pasando el mensaje al brazo robótico para enviarlo a {numero_telefono}...")
    enviar_mensaje_whatsapp(numero_telefono, mensaje_redactado)


# ZONA DE PRUEBAS
if __name__ == "__main__":
    # 1. Pon tu número de celular otra vez (con el 521...) para recibir la prueba
    mi_numero = "5217713308760"

    # 2. Inventemos una empresa objetivo para ver cómo la IA adapta el texto
    empresa_prueba = "Agroindustrias del Bajío"

    prospectar_empresa(empresa_prueba, mi_numero)