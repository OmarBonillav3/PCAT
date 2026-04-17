# PCAT — Instrucciones de instalación

## Paso 1: Compilar PCAT.exe

Necesitas Python instalado en tu PC solo para compilar (no para correrlo).

```bash
pip install pyinstaller zeroconf
pyinstaller --onefile --noconsole pcat.py --name PCAT
```

El .exe queda en la carpeta `dist/PCAT.exe`.
Muévelo a donde quieras, por ejemplo: `C:\PCAT\PCAT.exe`

---

## Paso 2: Configurar PCAT.exe

Antes de compilar, edita estas dos líneas en pcat.py:

```python
PORT  = 7070
TOKEN = "pcat-token-secreto-cambiame-2024"  # cambia esto por algo tuyo
```

---

## Paso 3: Autoarranque silencioso con Windows

1. Abre **Task Scheduler** (Programador de tareas)
2. Click en "Create Basic Task"
3. Nombre: `PCAT`
4. Trigger: **When the computer starts**
5. Action: **Start a program** → selecciona `C:\PCAT\PCAT.exe`
6. En "Finish", marca **"Open the Properties dialog"**
7. En Properties → pestaña **General** → marca **"Run whether user is logged on or not"**
8. Marca también **"Run with highest privileges"**
9. Click OK

PCAT.exe arranca automáticamente con Windows, sin ventana, sin icono.

---

## Paso 4: Abrir el puerto en el Firewall de Windows

Corre esto en PowerShell como administrador:

```powershell
New-NetFirewallRule -DisplayName "PCAT" -Direction Inbound -Protocol TCP -LocalPort 7070 -Action Allow
```

---

## Paso 5: Sin configuración de router necesaria

PCAT.exe se anuncia automáticamente en tu red como **`pcat.local`** via mDNS. El NodeMCU lo encuentra por ese nombre sin importar qué IP tenga tu PC ese día. No necesitas tocar el router.

El único requisito es que tu PC y el NodeMCU estén en la misma red WiFi.

---

## Paso 6: Subir el script al NodeMCU

1. Flashea Tasmota en el NodeMCU (via browser con tasmota.github.io/install)
2. Conéctalo a tu WiFi
3. Entra al panel web de Tasmota → **Tools → Berry Scripting Console**
4. Sube el archivo `autoexec.be`
5. Edita las variables al inicio:
   - `PC_IP`    → IP fija de tu PC
   - `PC_TOKEN` → mismo token que pusiste en pcat.py

---

## Uso

| Acción | Desde |
|--------|-------|
| Encender PC | App celular → activa el switch → pulso en PWR_SW |
| Apagar PC limpio | App celular → comando `pcat_off` → PCAT.exe hace shutdown |
| Reiniciar | Comando `pcat_restart` |
| Verificar si está encendida | Comando `pcat_ping` |
| Alexa | "Alexa, enciende la PC" (Tasmota Hue emulation) |

---

## Endpoints PCAT.exe

```
GET  http://IP:7070/ping
POST http://IP:7070/action
     Body: {"token": "tu-token", "action": "shutdown|restart|sleep"}
```
