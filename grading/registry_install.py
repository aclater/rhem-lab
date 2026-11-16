"""Grading for the registry-install exercise: install a registry."""
from .core import *  # noqa: F401,F403

NUM = 5
NAME = "registry-install"
TITLE = "Install a registry"


def grade():
    m = Exercise(NUM, NAME, TITLE)
    if not need_rhem(m):
        return m
    f = rhem()
    if not m.check(f.get("quay") == "active", "The mirror registry is running (quay-app)", "Run the mirror-registry install from step 2."):
        return m
    m.check(f.get("public"), "New repositories are public (CREATE_PRIVATE_REPO_ON_PUSH: false)",
            "Add that line to /opt/quay/quay-config/config.yaml and restart quay-app (step 3).")
    m.check(f.get("reg_trust") == "200", "The server VM trusts the registry's CA",
            "sudo install -m 0644 /opt/quay/quay-rootCA/rootCA.pem /etc/pki/ca-trust/source/anchors/lab-registry-ca.crt && sudo update-ca-trust")
    m.check(f.get("reg_login") == "admin", "root's podman is logged in to the registry as admin",
            "sudo podman login --authfile /root/.config/containers/auth.json -u admin -p edgelab123 rhem.lab.internal:8443 "
            "(a login made without --authfile is lost when the server restarts)")
    rc, code = run(["curl", "-k", "-s", "-m", "8", "-o", "/dev/null", "-w", "%{http_code}",
                    "--resolve", f"rhem.lab.internal:8443:{SUBNET}.10", "https://rhem.lab.internal:8443/"])
    m.check(code == "200", "The registry's web page answers from the workstation (https://rhem.lab.internal:8443)",
            "The lab network must be up and quay-app running: virsh -c qemu:///system net-list, then systemctl is-active quay-app on the server.")
    return m
