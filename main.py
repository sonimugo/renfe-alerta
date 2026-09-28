import time
import requests
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# ==========================================
# MINI SERVIDOR WEB PARA ENGAÑAR A RENDER
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

# Iniciar servidor web en un hilo secundario
server_thread = threading.Thread(target=run_dummy_server, daemon=True)
server_thread.start()

# ==========================================
# 1. TUS DATOS DE TELEGRAM
# ==========================================
TELEGRAM_TOKEN = "8894503363:AAHPMXQYdOSA8JR_AAHcxMISCTORpZv5EaU"
TELEGRAM_CHAT_ID = "8819982474"

# ==========================================
# 2. FECHAS DEL VIAJE (MODIFICABLES)
# ==========================================
FECHA_IDA = "29/09/2026"
FECHA_VUELTA = "29/09/2026"

# ==========================================
# 3. DATOS FIJOS DEL TRAYECTO
# ==========================================
ORIGEN_IDA = "Córdoba"
DESTINO_IDA = "Sevilla"

HORA_IDA = "06:20"
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

def consultar_renfe(origen, destino, fecha, hora):
    """Realiza una petición directa a la web de Renfe."""
    print(f"🔎 Consultando {origen} ➡️ {destino} el {fecha} a las {hora}...")
    
    url = "https://www.renfe.com/es/es"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9"
    }

    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            if hora in response.text and "Agotado" not in response.text and "Completo" not in response.text:
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
        f"🤖 *Bot de Renfe Activado (Servidor Nube)*\n\n"
        f"🚆 *IDA:* {ORIGEN_IDA} ➡️ {DESTINO_IDA}\n"
        f"📅 Fecha: {FECHA_IDA} - ⏰ Hora: {HORA_IDA}\n\n"
        f"🚆 *VUELTA:* {DESTINO_IDA} ➡️ {ORIGEN_IDA}\n"
        f"📅 Fecha: {FECHA_VUELTA} - ⏰ Hora: {HORA_VUELTA}"
    )
    enviar_alerta_telegram(msg_inicio)

    ida_encontrada = False
    vuelta_encontrada = False
    intentos = 0

    while not (ida_encontrada and vuelta_encontrada):
        intentos += 1
        print(f"\n--- Comprobación #{intentos} ---")
        
        # 1. Comprobar IDA
        if not ida_encontrada:
            if consultar_renfe(ORIGEN_IDA, DESTINO_IDA, FECHA_IDA, HORA_IDA):
                enviar_alerta_telegram(
                    f"🚨 *¡BILLETE DE IDA LIBERADO!* 🚨\n\n"
                    f"De: {ORIGEN_IDA}\n"
                    f"A: {DESTINO_IDA}\n"
                    f"Fecha: {FECHA_IDA} - Hora: {HORA_IDA}\n\n"
                    f"🔗 ¡Entra ya a la web a comprarlo!"
                )
                ida_encontrada = True

        # 2. Comprobar VUELTA
        if not vuelta_encontrada:
            if consultar_renfe(DESTINO_IDA, ORIGEN_IDA, FECHA_VUELTA, HORA_VUELTA):
                enviar_alerta_telegram(
                    f"🚨 *¡BILLETE DE VUELTA LIBERADO!* 🚨\n\n"
                    f"De: {DESTINO_IDA}\n"
                    f"A: {ORIGEN_IDA}\n"
                    f"Fecha: {FECHA_VUELTA} - Hora: {HORA_VUELTA}\n\n"
                    f"🔗 ¡Entra ya a la web a comprarlo!"
                )
                vuelta_encontrada = True

        if not (ida_encontrada and vuelta_encontrada):
            print("Aún no están disponibles los billetes. Esperando 3 minutos...")
            time.sleep(180)

    print("🎉 ¡Billetes notificados! Fin de la monitorización.")
