"""
PCAT Agent — Flask web server
Serves the config UI and exposes the REST API for script execution.
Run directly for development; imported by pcat_service.py for Windows Service mode.
"""

import json
import os
import re
import socket
import subprocess
import platform
import time
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="web")

BASE_DIR = Path(__file__).parent
SCRIPTS_FILE = BASE_DIR / "scripts.json"
START_TIME = time.time()

# On non-Windows platforms (dev on macOS/Linux) this flag doesn't exist.
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


# ── helpers ──────────────────────────────────────────────────────────────────

def _load_scripts() -> dict:
    if not SCRIPTS_FILE.exists():
        return {}
    with open(SCRIPTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_scripts(scripts: dict) -> None:
    with open(SCRIPTS_FILE, "w", encoding="utf-8") as f:
        json.dump(scripts, f, indent=2)


def _slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    return slug.strip("-") or "script"


def _unique_id(base: str, existing: dict) -> str:
    if base not in existing:
        return base
    counter = 2
    while f"{base}-{counter}" in existing:
        counter += 1
    return f"{base}-{counter}"


# ── static UI ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("web", "index.html")


# ── REST API ─────────────────────────────────────────────────────────────────

@app.route("/scripts", methods=["GET"])
def list_scripts():
    return jsonify(list(_load_scripts().values()))


@app.route("/scripts", methods=["POST"])
def add_script():
    data = request.get_json(silent=True) or {}
    missing = [k for k in ("name", "path", "type") if not data.get(k)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    valid_types = ("powershell", "bat", "python", "exe")
    if data["type"] not in valid_types:
        return jsonify({"error": f"type must be one of: {', '.join(valid_types)}"}), 400

    scripts = _load_scripts()
    script_id = _unique_id(_slugify(data["name"]), scripts)

    entry = {
        "id": script_id,
        "name": data["name"].strip(),
        "path": data["path"].strip(),
        "type": data["type"],
    }
    scripts[script_id] = entry
    _save_scripts(scripts)
    return jsonify(entry), 201


@app.route("/scripts/<script_id>", methods=["DELETE"])
def delete_script(script_id):
    scripts = _load_scripts()
    if script_id not in scripts:
        return jsonify({"error": "Script not found"}), 404
    del scripts[script_id]
    _save_scripts(scripts)
    return "", 204


@app.route("/execute/<script_id>", methods=["POST"])
def execute_script(script_id):
    # Always reload from disk so new scripts are available without restart.
    scripts = _load_scripts()
    if script_id not in scripts:
        return jsonify({"error": "Script not found"}), 404

    script = scripts[script_id]
    path = script["path"]
    kind = script["type"]

    if not os.path.exists(path):
        return jsonify({"error": f"File not found: {path}"}), 404

    type_to_cmd = {
        "powershell": ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", path],
        "bat":        ["cmd.exe", "/c", path],
        "python":     ["python", path],
        "exe":        [path],
    }
    cmd = type_to_cmd.get(kind)
    if cmd is None:
        return jsonify({"error": f"Unknown type: {kind}"}), 400

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            creationflags=CREATE_NO_WINDOW,
        )
        return jsonify({
            "id":         script_id,
            "name":       script["name"],
            "returncode": result.returncode,
            "stdout":     result.stdout,
            "stderr":     result.stderr,
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Timed out after 60 seconds"}), 408
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/status", methods=["GET"])
def status():
    try:
        import psutil
        system_uptime = int(time.time() - psutil.boot_time())
    except Exception:
        system_uptime = None

    return jsonify({
        "status":                "running",
        "hostname":              socket.gethostname(),
        "agent_uptime_seconds":  int(time.time() - START_TIME),
        "system_uptime_seconds": system_uptime,
        "platform":              platform.system(),
        "python_version":        platform.python_version(),
    })


# ── dev entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"PCAT Agent running at http://127.0.0.1:8080")
    app.run(host="127.0.0.1", port=8080, debug=False, use_reloader=False)
