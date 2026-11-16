#!/usr/bin/env python3
"""Serve the guide on this machine only, in the background.

  serve.py start [PORT]   start the server (port 8765, or the next free one) and print its address
  serve.py stop           stop it
  serve.py status         say whether it is running, and where
"""
import functools
import http.server
import json
import os
import pathlib
import signal
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "site"
STATE = ROOT / ".serve-state"      # {"pid": ..., "port": ...} while a server is running
LOG = ROOT / ".serve.log"


def running():
    """Return the state of a live server started from this folder, or None."""
    try:
        state = json.loads(STATE.read_text())
        os.kill(state["pid"], 0)
        cmdline = pathlib.Path(f"/proc/{state['pid']}/cmdline").read_bytes()
        if b"serve.py" not in cmdline:      # the PID was reused by something else
            raise ProcessLookupError
        return state
    except (OSError, ValueError, KeyError):
        STATE.unlink(missing_ok=True)
        return None


def run(first):
    """The background process: bind the first free port, record it, serve until stopped."""
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SITE))
    for port in range(first, first + 20):
        try:
            server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
        except OSError:
            continue
        STATE.write_text(json.dumps({"pid": os.getpid(), "port": port}))
        signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
        try:
            server.serve_forever()
        finally:
            STATE.unlink(missing_ok=True)
        return
    sys.exit(f"no free port between {first} and {first + 19}")


def start(first):
    state = running()
    if state:
        print(f"The guide is already being served: http://127.0.0.1:{state['port']}/")
        return
    with open(LOG, "ab") as log:
        subprocess.Popen([sys.executable, __file__, "_run", str(first)], stdin=subprocess.DEVNULL,
                         stdout=log, stderr=log, start_new_session=True)
    for _ in range(50):
        state = running()
        if state:
            if state["port"] != first:
                print(f"Port {first} is in use, so the guide is on port {state['port']}.")
            print(f"Guide: http://127.0.0.1:{state['port']}/")
            print(f"It keeps running in the background. Stop it with: make -C {ROOT} stop")
            return
        time.sleep(0.1)
    sys.exit(f"The server did not start. No free port between {first} and {first + 19}? See {LOG}. "
             f"Try another starting port: make -C {ROOT} serve PORT=9000")


def stop():
    state = running()
    if not state:
        print("The guide is not being served.")
        return
    os.kill(state["pid"], signal.SIGTERM)
    for _ in range(30):
        if not running():
            break
        time.sleep(0.1)
    print("Stopped.")


def status():
    state = running()
    print(f"Guide: http://127.0.0.1:{state['port']}/" if state else "The guide is not being served.")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "start"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8765
    {"start": lambda: start(port), "_run": lambda: run(port), "stop": stop, "status": status}.get(
        command, lambda: sys.exit(__doc__))()
