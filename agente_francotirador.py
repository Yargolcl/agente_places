import pandas as pd
import re
import time
import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import WebBaseLoader
import os
os.environ['USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'

# ==========================================
# CONFIGURACIÓN DEL FRANCOTIRADOR
# ==========================================
FILE_PATH = 'Z_Archivo_Pruebas/Base_Validada_Abarrotes_Pachuca.csv'  # Leemos lo que nos dejó la Fase 1
OUTPUT_PATH = 'Z_Archivo_Pruebas/Base_Lista_Para_GreenApi.csv'


# ==========================================
# FUNCIONES DE EXTRACCIÓN (REGEX)
# ==========================================
def extract_emails(text):
    """Busca patrones de correo electrónico en el texto."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    # Retorna correos únicos y elimina falsos positivos comunes como terminaciones en .png
    valid_emails = list(set([e.lower() for e in emails if not e.endswith(('.png', '.jpg', '.jpeg', '.gif'))]))
    return ", ".join(valid_emails) if valid_emails else "Sin Correo"


def extract_whatsapp_links(soup):
    """Busca botones o enlaces directos a WhatsApp en el código fuente."""
    wa_links = []
    # Buscar en todas las etiquetas <a> el atributo href
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'wa.me/' in href or 'api.whatsapp.com/send' in href:
            # Limpiar el link para dejar solo el número si es posible
            wa_links.append(href)
    return ", ".join(list(set(wa_links))) if wa_links else "Sin Link Directo"


# ==========================================
# MOTOR PRINCIPAL
# ==========================================
def main():
    print("Iniciando Francotirador Web (Extracción LangChain)...")

    # 1. Cargar la base validada
    df = pd.read_csv(FILE_PATH, encoding='utf-8')

    # Listas para guardar la nueva munición
    correos_extraidos = []
    whatsapp_extraidos = []

    # 2. Iterar solo sobre los que SÍ tienen sitio web
    for index, row in df.iterrows():
        website = str(row.get('Website_Google', 'Sin Web'))
        razon_social = row['Razon_Social']

        # Variables temporales para asegurar que SOLO agregamos 1 dato por fila
        current_emails = 'N/A'
        current_wa = 'N/A'

        # Si no hay web o es de Facebook, lo saltamos
        if website not in ['Sin Web', 'No Encontrado', 'Error'] and 'facebook.com' not in website:
            print(f"\n[+] Infiltrando: {website} ({razon_social})")
            try:
                # A) Cazar links de WhatsApp
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0'}
                response = requests.get(website, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                current_wa = extract_whatsapp_links(soup)

                # B) Cazar correos con LangChain
                loader = WebBaseLoader(website, requests_kwargs={'timeout': 10})
                docs = loader.load()
                texto_limpio = docs[0].page_content if docs else ""
                current_emails = extract_emails(texto_limpio)

                if current_emails == "Sin Correo":
                    print("    -> Correo no encontrado en portada.")

                print(f"    -> Correos: {current_emails}")
                print(f"    -> WhatsApp: {current_wa}")

            except Exception as e:
                print(f"    -> Error al infiltrar {website}: {str(e)[:50]}...")
                current_emails = 'Error de Conexión'
                current_wa = 'Error de Conexión'

        # C) GUARDA EXACTAMENTE UNA VEZ POR FILA (Aquí estaba el bug, ya está arreglado)
        correos_extraidos.append(current_emails)
        whatsapp_extraidos.append(current_wa)

        time.sleep(1)

    # 3. Guardar el botín en la base de datos
    df['Correos_Scrapeados'] = correos_extraidos
    df['WhatsApp_Scrapeado'] = whatsapp_extraidos

    # 4. Exportar el archivo final
    df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8')
    print(f"\n¡Operación exitosa! Base lista para Meta Ads y Amparo guardada en: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()