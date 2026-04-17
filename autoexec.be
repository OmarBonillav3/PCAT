# ─────────────────────────────────────────────────────────────
#  PCAT NodeMCU — Firmware Tasmota (Berry Script)
#  Archivo: autoexec.be  →  sube esto a Tasmota en Tools > Berry
# ─────────────────────────────────────────────────────────────
#
#  Conexiones:
#    D1 (GPIO5) → PWR_SW Pin 1 de la motherboard
#    GND        → PWR_SW Pin 2 de la motherboard
#
#  CONFIGURACION — edita estas variables:
#    PC_HOST  = nombre mDNS de tu PC (default: pcat.local, no necesitas tocar el router)
#    PC_PORT  = puerto donde corre PCAT.exe (default 7070)
#    PC_TOKEN = mismo token que pusiste en pcat.py
# ─────────────────────────────────────────────────────────────

var PC_HOST  = "pcat.local"      # se resuelve automaticamente, sin tocar el router
var PC_PORT  = 7070
var PC_TOKEN = "pcat-token-secreto-cambiame-2024"  # <-- mismo que pcat.py
var PWR_PIN  = 5                 # GPIO5 = D1

# ── Pulso en el boton de power (encender / forzar apagado) ──
def power_pulse()
  gpio.digital_write(PWR_PIN, 1)
  tasmota.delay(500)             # 500ms = encendido normal
  gpio.digital_write(PWR_PIN, 0)
  print("PCAT: pulso power enviado")
end

# ── Apagado limpio via PCAT.exe ──
def shutdown_pc()
  var body = '{"token":"' + PC_TOKEN + '","action":"shutdown"}'
  var url  = "http://" + PC_HOST + ":" + str(PC_PORT) + "/action"

  var cl = webclient()
  cl.begin(url)
  cl.add_header("Content-Type", "application/json")
  var code = cl.POST(body)

  if code == 200
    print("PCAT: apagado limpio enviado OK")
  else
    print("PCAT: error al contactar PCAT.exe, codigo=" + str(code))
    print("PCAT: intentando pulso largo de emergencia (4s)")
    gpio.digital_write(PWR_PIN, 1)
    tasmota.delay(4000)          # 4s = forzar apagado por hardware
    gpio.digital_write(PWR_PIN, 0)
  end
  cl.close()
end

# ── Reinicio via PCAT.exe ──
def restart_pc()
  var body = '{"token":"' + PC_TOKEN + '","action":"restart"}'
  var url  = "http://" + PC_HOST + ":" + str(PC_PORT) + "/action"

  var cl = webclient()
  cl.begin(url)
  cl.add_header("Content-Type", "application/json")
  var code = cl.POST(body)

  if code == 200
    print("PCAT: reinicio enviado OK")
  else
    print("PCAT: error al contactar PCAT.exe, codigo=" + str(code))
  end
  cl.close()
end

# ── Ping: verifica si la PC esta encendida ──
def ping_pc()
  var url = "http://" + PC_HOST + ":" + str(PC_PORT) + "/ping"
  var cl = webclient()
  cl.begin(url)
  var code = cl.GET()
  cl.close()
  if code == 200
    print("PCAT: PC online")
    return true
  else
    print("PCAT: PC offline o PCAT.exe no responde")
    return false
  end
end

# ── Comandos MQTT / Consola Tasmota ──
# Desde la consola de Tasmota puedes escribir:
#   pcat_on      → enciende la PC (pulso)
#   pcat_off     → apagado limpio via PCAT.exe
#   pcat_restart → reinicio limpio
#   pcat_ping    → verifica si la PC esta encendida
#
# Desde Alexa / app / regla:
#   Rule: ON Power1#State=1 DO Backlog pcat_on ENDON
#   (configura en Tasmota Rules)

tasmota.add_cmd("pcat_on",      def(cmd, idx, payload) power_pulse() end)
tasmota.add_cmd("pcat_off",     def(cmd, idx, payload) shutdown_pc() end)
tasmota.add_cmd("pcat_restart", def(cmd, idx, payload) restart_pc()  end)
tasmota.add_cmd("pcat_ping",    def(cmd, idx, payload) ping_pc()     end)

# ── Setup del pin ──
gpio.pin_mode(PWR_PIN, gpio.OUTPUT)
gpio.digital_write(PWR_PIN, 0)

print("PCAT NodeMCU listo. Comandos: pcat_on / pcat_off / pcat_restart / pcat_ping")
