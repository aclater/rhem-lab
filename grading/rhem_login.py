"""Grading for the rhem-login exercise: log in for the first time."""
from .core import *  # noqa: F401,F403

NUM = 4
NAME = "rhem-login"
TITLE = "Log in for the first time"


def grade():
    m = Exercise(NUM, NAME, TITLE)
    if not need_rhem(m):
        return m
    f = rhem()
    m.check("flightctl-admin" in f.get("admin_groups", "").split(), "User admin exists in group flightctl-admin",
            "Create it inside the flightctl-pam-issuer container (step 1).")
    m.check(f.get("ui_trust") == "200", "The server VM trusts the lab CA",
            "sudo install -m 0644 /etc/flightctl/pki/ca.crt /etc/pki/ca-trust/source/anchors/rhem-lab-ca.crt && sudo update-ca-trust")
    m.check(f.get("login"), "flightctl is logged in on the server VM", "flightctl login https://rhem.lab.internal --username admin --password edgelab123  (logins expire; log in again)")
    v = f.get("versions", "")
    m.check(v.count("v1.4") >= 2, "Client and server are both version 1.4", f"flightctl version reports: {v.strip() or 'nothing (not logged in)'}")
    rc, out = run(["getent", "ahostsv4", "rhem.lab.internal"])
    address = out.split()[0] if rc == 0 and out.split() else ""
    if m.check(address == f"{SUBNET}.10", f"The workstation resolves rhem.lab.internal (found {address or 'nothing'})",
               "On the workstation: sudo resolvectl dns virbr-rhem 192.168.160.1 and sudo resolvectl domain virbr-rhem '~lab.internal' "
               "(step 5). The setting is lost when the lab network or the workstation restarts."):
        rc, code = run(["curl", "-k", "-s", "-m", "8", "-o", "/dev/null", "-w", "%{http_code}", "https://rhem.lab.internal/"])
        m.check(code == "200", "The web UI answers from the workstation (https://rhem.lab.internal)",
                "The name resolves but the UI did not answer. Is flightctl.target active on the server?")
    return m
