# PCAT — Roadmap & Ideas

> Cosas pendientes, features que quiero agregar y dirección del proyecto.
> Actualizar a medida que avance.

---

## Hardware pendiente

- [ ] Recibir el NodeMCU ESP8266 y hacer las primeras pruebas reales
- [ ] Imprimir el case STL y montarlo dentro del chasis
- [ ] Instalar el bracket USB-C PCI y pasar el cable al exterior
- [ ] Conectar los 2 cables del ESP al header PWR_SW de la placa madre
- [ ] Flashear Tasmota y subir `autoexec.be` con el token correcto
- [ ] Verificar que `pcat.local` se resuelve bien por mDNS desde el ESP

---

## Agent · PC (pcat_agent.py)

- [ ] **Voz en Windows** — usar la API de Windows Speech Recognition para disparar
      scripts con comandos de voz sin necesidad del ESP ni el celular.
      (`speech_recognition` + `pywin32` o Windows SAPI directo)
- [ ] **Puerto dedicado para config** — mover la web UI de config a un puerto
      separado (ej. `:8081`) para que el `:8080` quede limpio solo para la API
      que llama el ESP
- [ ] **Claude Code en PCAT** — integrar la API de Claude para poder darle
      instrucciones en lenguaje natural desde la web UI o por voz y que PCAT
      decida qué script ejecutar o genere uno nuevo al vuelo
- [ ] Agregar campo opcional `description` a cada script en `scripts.json`
- [ ] Log de ejecuciones — guardar historial de qué script se corrió, cuándo y
      con qué resultado (stdout/stderr + returncode)
- [ ] Notificación de resultado — mandar una notificación de Windows toast
      cuando un script termina de ejecutarse
- [ ] Scripts con parámetros — poder pasar argumentos al momento de ejecutar,
      no solo un path fijo
- [ ] Timeout configurable por script (hoy está fijo en 60s)
- [ ] Endpoint `GET /logs` para ver el historial desde la web UI

---

## Agent · Windows Service (pcat_service.py)

- [ ] Probar install/start/stop/remove en una máquina Windows real
- [ ] Verificar que el servicio arranca antes de que el usuario inicie sesión
- [ ] Agregar watchdog: si Flask se cae, que el servicio lo reinicie solo

---

## ESP8266 · Tasmota / Berry (autoexec.be)

- [ ] Escribir el `autoexec.be` con los primeros comandos reales (power on/off,
      ping, execute script por ID)
- [ ] Probar la integración ESP → `POST /execute/{id}` → respuesta en el ESP
- [ ] Explorar CSS override en Tasmota para que la UI del ESP tenga el mismo
      estilo que el agente (colores paper/accent de PCAT)
- [ ] Evaluar páginas custom con `webserver.on()` en Berry para tener una mini
      UI de control directo desde el ESP

---

## Integraciones

- [ ] **Alexa** — via Tasmota Hue emulation, "Alexa, enciende la PC"
- [ ] **App celular** — definir qué app se usa para mandar comandos
      (Tasmota app, HTTP Shortcuts, o app propia a futuro)
- [ ] **Home Assistant** — evaluar integración para meter PCAT en los
      automations del hogar
- [ ] Trigger desde Shortcuts de iOS/Android para ejecutar scripts directamente

---

## Web UI (web/index.html)

- [ ] Vista de logs de ejecución en la misma web
- [ ] Indicador visual mientras un script está corriendo (estado en tiempo real)
- [ ] Reordenar scripts con drag & drop
- [ ] Poder editar un script ya registrado (nombre, path, tipo) sin borrarlo
- [ ] Búsqueda/filtro en la lista de scripts cuando haya muchos

---

## Ideas a largo plazo

- [ ] **PCAT como plataforma** — que cualquier dispositivo en la red local
      (no solo el ESP) pueda llamar a `POST /execute/{id}`
- [ ] Crear una app móvil propia con el estilo visual de PCAT
- [ ] Marketplace de scripts — colección de scripts útiles listos para importar
- [ ] Modo multi-PC — un ESP controlando más de una PC en la red
- [ ] PCAT como skill de Alexa real (no solo Hue emulation)

---

## Completado ✓

- [x] Daemon HTTP básico en Python (`pcat.py`) con shutdown/restart/sleep
- [x] mDNS para que el ESP encuentre la PC como `pcat.local`
- [x] Case STL imprimible para el ESP dentro del chasis
- [x] Bracket USB-C PCI diseñado y linkado
- [x] Windows Service (`pcat_service.py`) con install/start/stop/remove
- [x] Flask agent con API REST completa (`/scripts`, `/execute`, `/status`)
- [x] Registry de scripts en `scripts.json` (lectura en caliente, sin reiniciar)
- [x] Web UI con estética editorial PCAT (Instrument Serif + JetBrains Mono)
