"""
PCAT Agent — Windows Service wrapper
Usage (run as Administrator):
  python pcat_service.py install   — register the service
  python pcat_service.py start     — start it
  python pcat_service.py stop      — stop it
  python pcat_service.py remove    — unregister it
  python pcat_service.py debug     — run interactively (no SCM, Ctrl+C to quit)
"""

import os
import sys
import threading

# Make sure imports resolve relative to this file's directory,
# regardless of the working directory Windows picks when launching the service.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import win32event
import win32service
import win32serviceutil
import servicemanager


class PCATService(win32serviceutil.ServiceFramework):
    _svc_name_         = "PCATAgent"
    _svc_display_name_ = "PCAT Agent"
    _svc_description_  = (
        "PC Automation & Control Agent. "
        "Exposes a local HTTP API on port 8080 for script execution."
    )

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self._stop_event = win32event.CreateEvent(None, 0, 0, None)
        self._flask_thread = None

    # ── SCM callbacks ─────────────────────────────────────────────────────────

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ""),
        )
        self._flask_thread = threading.Thread(
            target=self._run_flask, daemon=True, name="pcat-flask"
        )
        self._flask_thread.start()

        # Block until SvcStop sets the event.
        win32event.WaitForSingleObject(self._stop_event, win32event.INFINITE)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STOPPED,
            (self._svc_name_, ""),
        )
        win32event.SetEvent(self._stop_event)
        # Flask's dev server has no clean shutdown hook; daemon thread exits
        # automatically once the main service thread unblocks and returns.

    # ── internal ──────────────────────────────────────────────────────────────

    def _run_flask(self):
        from pcat_agent import app
        app.run(host="127.0.0.1", port=8080, debug=False, use_reloader=False)


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Launched by the SCM with no arguments — hand off to dispatcher.
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(PCATService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # install / start / stop / remove / debug
        win32serviceutil.HandleCommandLine(PCATService)
