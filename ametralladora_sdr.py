import csv
import time
import random
from herramienta_whatsapp import enviar_mensaje_whatsapp

# La nueva Pista de Aterrizaje
archivo_bd = "2_Pipeline_SDR.csv"


def limpiar_numero(telefono_bruto):
    numeros_solo = ''.join(filter(str.isdigit, str(telefono_bruto)))
    if numeros_solo.startswith("52") and len(numeros_solo) > 10:
        numeros_solo = numeros_solo[2:]
    if len(numeros_solo) == 10:
        return f"521{numeros_solo}"
    return numeros_solo


def cazador_sdr():
    print("🔫 Cazador SDR Activado. Preparando municiones y leyendo memoria...")
    filas_actualizadas = []

    try:
        # 1. Leemos el archivo y lo blindamos (como le enseñamos al Guardia)
        with open(archivo_bd, mode='r', encoding='utf-8-sig') as archivo:
            lector = csv.DictReader(archivo)
            nombres_columnas = [str(col).strip() for col in lector.fieldnames] if lector.fieldnames else []

            if "Estatus" not in nombres_columnas:
                nombres_columnas.append("Estatus")

            for fila_bruta in lector:
                fila = {str(k).strip(): str(v).strip() if v else "" for k, v in fila_bruta.items()}
                if "Estatus" not in fila:
                    fila["Estatus"] = ""
                filas_actualizadas.append(fila)

        # 2. Empezamos la ronda de disparos
        for fila in filas_actualizadas:
            numero_original = fila.get("Telefono_Google", "")
            estatus = fila.get("Estatus", "")
            razon_social = fila.get("Razon_Social", "su empresa")

            # EL FILTRO MAESTRO: Solo dispara si NO hay un estatus previo
            if numero_original and estatus == "":
                numero_limpio = limpiar_numero(numero_original)

                print(f"\n🎯 Apuntando a: {razon_social}")
                rompehielos = f"Hola, ¿este es el celular de operaciones de {razon_social}?"

                # Disparamos
                enviar_mensaje_whatsapp(numero_limpio, rompehielos)

                # Documentamos en la memoria interna
                fila["Estatus"] = "Rompehielos Enviado"

                # Pausa táctica anti-baneo de Meta (entre 8 y 15 segundos)
                pausa = random.randint(8, 15)
                print(f"⏳ Pausa táctica de {pausa} segundos para simular comportamiento humano...")
                time.sleep(pausa)

            elif estatus != "":
                print(f"⏩ Saltando a {razon_social}. Su estatus actual es: {estatus}")

        # 3. Guardamos los resultados finales en el Excel
        with open(archivo_bd, mode='w', newline='', encoding='utf-8-sig') as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=nombres_columnas)
            escritor.writeheader()
            escritor.writerows(filas_actualizadas)

        print("\n✅ Misión del Cazador completada. Base de datos actualizada.")

    except Exception as e:
        print(f"⚠️ Error crítico en el Cazador: {e}")


if __name__ == "__main__":
    cazador_sdr()