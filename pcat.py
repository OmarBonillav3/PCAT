"""
PCAT.exe — PC Agent Tool
Servidor HTTP minimalista para control remoto de apagado/reinicio.
Corre en background, sin ventana, consumo minimo de recursos.
"""

import http.server
import threading
import subprocess
import os
import json
import hashlib
import socket
from datetime import datetime
from zeroconf import ServiceInfo, Zeroconf

# ─────────────────────────────────────────
#  CONFIGURACION — edita esto antes de compilar
# ─────────────────────────────────────────
PORT     = 7070
HOSTNAME = "pcat"   # tu PC sera encontrada como pcat.local en la red
# Token secreto: cambialo por uno tuyo, cualquier texto largo y aleatorio
TOKEN    = "pcat-token-secreto-cambiame-2024"
# ─────────────────────────────────────────

VERSION = "1.0.0"

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def validate_token(token):
    return hashlib.sha256(token.encode()).hexdigest() == \
           hashlib.sha256(TOKEN.encode()).hexdigest()

class PCATHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Silencia el log por defecto del servidor HTTP
        pass

    def send_json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # Health check — para que Tasmota o la app verifiquen que PCAT esta vivo
        if self.path == "/ping":
            self.send_json(200, {"status": "ok", "version": VERSION})
            log("Ping recibido")
            return
        self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        length  = int(self.headers.get("Content-Length", 0))
        raw     = self.rfile.read(length)

        try:
            body = json.loads(raw)
        except:
            self.send_json(400, {"error": "JSON invalido"})
            return

        token = body.get("token", "")
        if not validate_token(token):
            self.send_json(403, {"error": "Token invalido"})
            log(f"Intento con token invalido desde {self.client_address[0]}")
            return

        action = body.get("action", "")

        if action == "shutdown":
            self.send_json(200, {"status": "shutting down"})
            log(f"Apagado solicitado desde {self.client_address[0]}")
            threading.Timer(1.5, lambda: os.system("shutdown /s /t 0")).start()

        elif action == "restart":
            self.send_json(200, {"status": "restarting"})
            log(f"Reinicio solicitado desde {self.client_address[0]}")
            threading.Timer(1.5, lambda: os.system("shutdown /r /t 0")).start()

        elif action == "sleep":
            self.send_json(200, {"status": "sleeping"})
            log(f"Suspender solicitado desde {self.client_address[0]}")
            threading.Timer(1.5, lambda: subprocess.run(
                ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"]
            )).start()

        else:
            self.send_json(400, {"error": f"Accion desconocida: {action}"})

def register_mdns(ip):
    """Anuncia pcat.local en la red via mDNS para que el NodeMCU siempre lo encuentre."""
    try:
        ip_bytes = socket.inet_aton(ip)
        info = ServiceInfo(
            "_http._tcp.local.",
            f"{HOSTNAME}._http._tcp.local.",
            addresses=[ip_bytes],
            port=PORT,
            properties={"version": VERSION},
            server=f"{HOSTNAME}.local.",
        )
        zc = Zeroconf()
        zc.register_service(info)
        log(f"mDNS activo: http://{HOSTNAME}.local:{PORT}")
        return zc
    except Exception as e:
        log(f"mDNS no disponible: {e}")
        return None

def main():
    ip = get_local_ip()

    log(f"PCAT v{VERSION} iniciando...")
    log(f"IP local:  http://{ip}:{PORT}")
    log(f"mDNS:      http://{HOSTNAME}.local:{PORT}")
    log(f"Endpoints:")
    log(f"  GET  /ping")
    log(f"  POST /action  {{token, action: shutdown|restart|sleep}}")

    zc = register_mdns(ip)

    server = http.server.HTTPServer(("0.0.0.0", PORT), PCATHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("PCAT detenido.")
        server.shutdown()
        if zc:
            zc.close()

if __name__ == "__main__":
    main()
