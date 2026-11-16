"""Grading for the rhem-install exercise: install Red Hat Edge Manager."""
from .core import *  # noqa: F401,F403

NUM = 3
NAME = "rhem-install"
TITLE = "Install Red Hat Edge Manager"


def grade():
    m = Exercise(NUM, NAME, TITLE)
    if not need_rhem(m):
        return m
    f = rhem()
    if (LAB / "offline").is_dir():
        # A disconnected install: packages and images come from the offline bundle, not from Red Hat's services.
        m.skip("Registration, the Red Hat repository and the registry login",
               "Not expected: ~/edgelab/offline exists, so this is a disconnected install.")
    else:
        m.check(f.get("registered"), "The server is registered with Red Hat",
                "In the server VM: sudo subscription-manager register --org <organization_id> --activationkey <activation_key> (step 1).")
        m.check(f.get("repo"), "The Edge Manager 1.4 repository is enabled",
                "sudo subscription-manager repos --enable edge-manager-1.4-for-rhel-9-x86_64-rpms")
        m.check(f.get("rh_auth"), "root's podman can log in to registry.redhat.io (/root/.config/containers/auth.json)",
                "Copy inputs/pull-secret.json to the VM and install it as /root/.config/containers/auth.json (step 4).")
    m.check(f.get("services", "").startswith("1.4"), f"flightctl-services 1.4 is installed (found {f.get('services') or 'none'})",
            "sudo dnf -y install flightctl-services flightctl-cli")
    m.check(f.get("cli", "").startswith("1.4"), f"flightctl-cli 1.4 is installed (found {f.get('cli') or 'none'})", "sudo dnf -y install flightctl-cli")
    m.check(f.get("basedomain") == "rhem.lab.internal", f"baseDomain is rhem.lab.internal (found {f.get('basedomain') or 'empty'})",
            "Set baseDomain in /etc/flightctl/service-config.yaml (step 5).")
    if m.check(f.get("target") == "active", "flightctl.target is started", "sudo systemctl enable --now flightctl.target"):
        m.check(f.get("unhealthy") == "0" and int(f.get("units") or 0) > 10,
                f"All Edge Manager services are healthy ({f.get('unhealthy', '?')} are not)",
                "Give it a few minutes on first start. Then: sudo journalctl -u flightctl-db -n 30")
        m.check(f.get("ui_ca") == "200", "The web UI answers on https://rhem.lab.internal/", "Services are still starting, or baseDomain was changed after the first start.")
    return m
