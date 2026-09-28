import time
import requests
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# ==========================================
# MINI SERVIDOR WEB PARA RENDER
# ==========================================
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot Renfe activo y ejecutandose.")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    server.serve_forever()

server_thread = threading.Thread(target=run_dummy_server, daemon=True)
server_thread.start()

# ==========================================
# 1. TUS DATOS DE TELEGRAM
# ==========================================
TELEGRAM_TOKEN = "8894503363:AAHPMXQYdOSA8JR_AAHcxMISCTORpZv5EaU"
TELEGRAM_CHAT_ID = "8819982474"

# ==========================================
# 2. FECHAS DEL VIAJE (DD/MM/AAAA)
# ==========================================
FECHA_IDA = "29/09/2026"
FECHA_VUELTA = "29/09/2026"

# ==========================================
# 3. DATOS FIJOS Y CÓDIGOS DE ESTACIÓN
# ==========================================
ORIGEN_NOMBRE = "Córdoba"
DESTINO_NOMBRE = "Sevilla-Santa Justa"

# Códigos oficiales de Renfe para las estaciones
CODIGO_CORDOBA = "50500"
CODIGO_SEVILLA = "51200"

HORA_IDA = "07:52"
HORA_VUELTA = "15:20"

def enviar_alerta_telegram(mensaje):
    """Envía un aviso instantáneo a tu móvil por Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': mensaje,
        'parse_mode': 'Markdown'
    }
    try:
        requests.post(url, data=payload, timeout=10)
        print("🔔 Alerta enviada a tu Telegram con éxito.")
    except Exception as e:
        print(f"Error al enviar mensaje a Telegram: {e}")

def consultar_renfe(cod_origen, cod_destino, fecha, hora_objetivo, nombre_orig, nombre_dest):
    """Consulta directamente el buscador de horarios de Renfe."""
    print(f"🔎 Consultando {nombre_orig} ➡️ {nombre_dest} para el {fecha} a las {hora_objetivo}...")
    
    url = "https://venta.renfe.com/vol/buscarTren.do"
    
    # Parámetros del formulario de búsqueda de Renfe
    payload = {
        'tipoBusqueda': 'VT',
        'cdgoOrigen': cod_origen,
        'cdgoDestino': cod_destino,
        'fecViaje': fecha,
        'adultos': '1',
        'ninos': '0',
        'tarjetaDorada': 'false'
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9"
    }

    try:
        session = requests.Session()
        response = session.post(url, data=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            html = response.text
            # Si la hora está en los resultados y no figura como agotado
            if hora_objetivo in html:
                # Comprobación básica de disponibilidad
                if "Agotado" not in html and "Completo" not in html:
                    return True
                else:
                    # Buscar si el bloque del tren específico tiene plazas
                    pos = html.find(hora_objetivo)
                    bloque = html[pos:pos+500]
                    if "Agotado" not in bloque and "sin plazas" not in bloque.lower():
                        return True
    except Exception as e:
        print(f"⚠️ Nota de conexión: {e}")

    return False

# ==========================================
# BUCLE PRINCIPAL DE MONITORIZACIÓN
# ==========================================
if __name__ == "__main__":
    print("🚀 Bot iniciado correctamente en Render.")
    
    msg_inicio = (
        f"🤖 *Bot de Renfe Reconfigurado y Activo*\n\n"
        f"🚆 *IDA:* {ORIGEN_NOMBRE} ➡️ {DESTINO_NOMBRE}\n"
        f"📅 Fecha: {FECHA_IDA} - ⏰ Hora: {HORA_IDA}\n\n"
        f"🚆 *VUELTA:* {DESTINO_NOMBRE} ➡️ {ORIGEN_NOMBRE}\n"
        f"📅 Fecha: {FECHA_VUELTA} - ⏰ Hora: {HORA_VUELTA}"
    )
    enviar_alerta_telegram(msg_inicio)

    ida_encontrada = False
    vuelta_encontrada = False
    intentos = 0

    while not (ida_encontrada and vuelta_encontrada):
        intentos += 1
        print(f"\n--- Comprobación #{intentos} ---")
        
        # 1. Comprobar IDA (Córdoba -> Sevilla)
        if not ida_encontrada:
            if consultar_renfe(CODIGO_CORDOBA, CODIGO_SEVILLA, FECHA_IDA, HORA_IDA, ORIGEN_NOMBRE, DESTINO_NOMBRE):
                enviar_alerta_telegram(
                    f"🚨 *¡BILLETE DE IDA LIBERADO!* 🚨\n\n"
                    f"De: {ORIGEN_NOMBRE}\n"
                    f"A: {DESTINO_NOMBRE}\n"
                    f"Fecha: {FECHA_IDA} - Hora: {HORA_IDA}\n\n"
                    f"🔗 ¡Entra ya a la web a comprarlo!"
                )
                ida_encontrada = True

        # 2. Comprobar VUELTA (Sevilla -> Córdoba)
        if not vuelta_encontrada:
            if consultar_renfe(CODIGO_SEVILLA, CODIGO_CORDOBA, FECHA_VUELTA, HORA_VUELTA, DESTINO_NOMBRE, ORIGEN_NOMBRE):
                enviar_alerta_telegram(
                    f"🚨 *¡BILLETE DE VUELTA LIBERADO!* 🚨\n\n"
                    f"De: {DESTINO_NOMBRE}\n"
                    f"A: {ORIGEN_NOMBRE}\n"
                    f"Fecha: {FECHA_VUELTA} - Hora: {HORA_VUELTA}\n\n"
                    f"🔗 ¡Entra ya a la web a comprarlo!"
                )
                vuelta_encontrada = True

        if not (ida_encontrada and vuelta_encontrada):
            print("Aún no están disponibles los billetes. Esperando 3 minutos...")
            time.sleep(180)

    print("🎉 ¡Billetes notificados! Fin de la monitorización.")
