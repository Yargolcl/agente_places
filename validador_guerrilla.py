import pandas as pd
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# ==========================================
# CONFIGURACIÓN
# ==========================================
FILE_PATH = 'Z_Archivo_Pruebas/Base_Lista_Para_Meta_Ads.csv'
OUTPUT_PATH = 'Z_Archivo_Pruebas/Base_Final_Oro_Puro.csv'


def formatear_mexico(tel):
    num = re.sub(r'\D', '', str(tel))
    if len(num) == 10: return f"52{num}"
    if len(num) == 12 and num.startswith('52'): return num
    return None


# ==========================================
# INICIO DEL NAVEGADOR
# ==========================================
print("Iniciando Navegador...")
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://web.whatsapp.com")

input("Presiona ENTER cuando ya veas tus chats de WhatsApp abiertos...")

# ==========================================
# PROCESAMIENTO
# ==========================================
df = pd.read_csv(FILE_PATH)
resultados = []

for index, row in df.iterrows():
    tel_raw = row.get('Telefono_Google', '')
    numero = formatear_mexico(tel_raw)

    if not numero:
        resultados.append("Formato Incorrecto")
        continue

    print(f"\nVerificando {numero} ({row['Razon_Social']})...")

    url = f"https://web.whatsapp.com/send?phone={numero}"
    driver.get(url)

    try:
        print("   ⏳ Escaneando transición de pantalla...")

        timeout = 20  # Aumentamos a 20 por si el internet de Pachuca fluctúa
        start_time = time.time()
        confirmado_si = False
        confirmado_no = False

        while time.time() - start_time < timeout:

            # 1. PRUEBA DE ÉXITO: ¿Ya puedo escribir?
            # Buscamos el cuadro de texto donde se redacta el mensaje
            try:
                # Este selector busca el área editable de escritura
                caja_texto = driver.find_elements(By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']")
                if len(caja_texto) > 0:
                    confirmado_si = True
                    break
            except:
                pass

            # 2. PRUEBA DE ERROR: ¿Apareció la ventana de 'no está en WhatsApp'?
            try:
                error_modal = driver.find_elements(By.XPATH, "//*[contains(text(), 'no está en WhatsApp')]")
                if len(error_modal) > 0:
                    # Esperamos un momento para ver si es el 'parpadeo' que mencionas
                    time.sleep(3)
                    # Volvemos a checar la caja de texto
                    caja_texto_retry = driver.find_elements(By.CSS_SELECTOR,
                                                            "div[contenteditable='true'][data-tab='10']")
                    if len(caja_texto_retry) > 0:
                        confirmado_si = True
                        break
                    else:
                        confirmado_no = True
                        # No hacemos break inmediato, dejamos que el bucle agote un poco más de tiempo
            except:
                pass

            time.sleep(1)

        # DECISIÓN FINAL
        if confirmado_si:
            print("   [+] ¡EXITO! Chat abierto correctamente.")
            resultados.append("SI")
        elif confirmado_no:
            print("   [-] FALLO: El número definitivamente no tiene WhatsApp.")
            resultados.append("NO")
            # Cerrar el modal para limpiar la pantalla
            try:
                driver.find_element(By.XPATH, "//button//div[contains(text(), 'OK')]").click()
            except:
                pass
        else:
            print("   [?] INDETERMINADO: Se agotó el tiempo de carga.")
            resultados.append("Revisar Manualmente")

    except Exception as e:
        print(f"   [!] Error: {e}")
        resultados.append("Error")

# Guardar y cerrar
df['WhatsApp_Validado'] = resultados
df.to_csv(OUTPUT_PATH, index=False)
driver.quit()
print(f"\nProceso terminado. Archivo guardado: {OUTPUT_PATH}")