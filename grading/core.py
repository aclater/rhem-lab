"""Shared pieces for the lab's grading scripts: where the lab lives, how to run things, how a step is recorded.

Everything here only reads. Nothing in the grading scripts changes the workstation or the lab VMs.
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

LAB = pathlib.Path(os.environ.get("EDGELAB", "~/edgelab")).expanduser()
# Names the guide uses. The environment variables exist so the checker itself can be tested
# against an environment built under other names.
NET = os.environ.get("CHECK_NET", "rhem-lab")
VM_PREFIX = os.environ.get("CHECK_VM_PREFIX", "")
SUBNET = os.environ.get("CHECK_SUBNET", "192.168.160")
SSH_CONFIG = pathlib.Path(os.environ.get("CHECK_SSH_CONFIG", LAB / "ssh_config"))
VIRSH = ["virsh", "-c", "qemu:///system"]
REGISTRY = "rhem.lab.internal:8443"
EDGES = ["edge-1", "edge-2", "edge-3"]
OFFLINE_FILES = ["rhem-bundle.tar.gz", "gateway-image.tar", "mirror-registry.tar.gz", "lab-images.tar"]


class Exercise:
    """The result of checking one exercise: an ordered list of steps.

    A step is (state, label, hint). state is "SUCCESS", "FAIL" or "SKIP" (could not be looked at yet).
    """

    def __init__(self, num, name, title):
        self.num, self.name, self.title, self.steps = num, name, title, []

    def ok(self, label):
        self.steps.append(("SUCCESS", label, ""))

    def fail(self, label, hint):
        self.steps.append(("FAIL", label, hint))

    def skip(self, label, why):
        self.steps.append(("SKIP", label, why))

    def check(self, condition, label, hint):
        """Record a step: SUCCESS if condition holds, otherwise FAIL with the hint. Returns the condition."""
        (self.ok(label) if condition else self.fail(label, hint))
        return bool(condition)

    @property
    def started(self):
        return any(s[0] == "SUCCESS" for s in self.steps)

    @property
    def passed(self):
        return self.started and not any(s[0] == "FAIL" for s in self.steps)

    @property
    def first_failure(self):
        return next((s for s in self.steps if s[0] == "FAIL"), None)


def run(cmd, timeout=40, stdin=None):
    """Run a command; return (exit code, stdout). Never raises."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, input=stdin)
        return p.returncode, p.stdout
    except (OSError, subprocess.TimeoutExpired):
        return 255, ""


def ssh(host, script, timeout=60):
    """Run a shell script inside a lab VM; return (exit code, stdout)."""
    cmd = ["ssh", "-F", str(SSH_CONFIG), "-o", "BatchMode=yes", "-o", "ConnectTimeout=6", host, "bash -s"]
    return run(cmd, timeout=timeout, stdin=script)


def facts(host, script):
    """Run a script that prints key=value lines; return them as a dict (empty if the VM is unreachable)."""
    rc, out = ssh(host, script)
    found = dict(line.split("=", 1) for line in out.splitlines() if "=" in line)
    found["_reachable"] = "yes" if rc != 255 else ""
    return found


def mode(path):
    return oct(path.stat().st_mode & 0o777)[2:]


def qemu_info(path):
    rc, out = run(["qemu-img", "info", "-U", "--output=json", str(path)])   # -U: the VM may be using the disk
    try:
        return json.loads(out) if rc == 0 else {}
    except ValueError:
        return {}


def vm_state(name):
    rc, out = run(VIRSH + ["domstate", VM_PREFIX + name])
    return out.strip() if rc == 0 else ""


def has_tabs(path):
    return any(line[: len(line) - len(line.lstrip())].count("\t") for line in path.read_text().splitlines())


def iso_label(path):
    try:
        with open(path, "rb") as f:
            f.seek(0x8000 + 40)
            return f.read(32).decode("ascii", "replace").strip()
    except OSError:
        return ""


RHEM_FACTS = r"""
sudo subscription-manager identity >/dev/null 2>&1 && echo registered=yes
sudo subscription-manager repos --list-enabled 2>/dev/null | grep -q edge-manager-1.4-for-rhel-9-x86_64-rpms && echo repo=yes
echo "services=$(rpm -q --qf '%{VERSION}' flightctl-services 2>/dev/null | grep -E '^[0-9]')"
echo "cli=$(rpm -q --qf '%{VERSION}' flightctl-cli 2>/dev/null | grep -E '^[0-9]')"
sudo grep -q '"registry.redhat.io"' /root/.config/containers/auth.json 2>/dev/null && echo rh_auth=yes
echo "basedomain=$(awk '/^ *baseDomain:/{print $2; exit}' /etc/flightctl/service-config.yaml 2>/dev/null)"
echo "target=$(systemctl is-active flightctl.target 2>/dev/null)"
echo "unhealthy=$(systemctl list-units 'flightctl*' --no-pager --plain --no-legend 2>/dev/null | grep -vcE 'active +(running|exited|active)')"
echo "units=$(systemctl list-units 'flightctl*' --no-pager --plain --no-legend 2>/dev/null | wc -l)"
echo "ui_ca=$(curl -s -m 8 -o /dev/null -w '%{http_code}' --cacert /etc/flightctl/pki/ca.crt https://rhem.lab.internal/ 2>/dev/null)"
echo "admin_groups=$(sudo podman exec flightctl-pam-issuer id -nG admin 2>/dev/null)"
echo "ui_trust=$(curl -s -m 8 -o /dev/null -w '%{http_code}' https://rhem.lab.internal/ 2>/dev/null)"
flightctl get devices >/dev/null 2>&1 && echo login=yes
echo "versions=$(flightctl version 2>/dev/null | tr '\n' ' ')"
echo "quay=$(systemctl is-active quay-app 2>/dev/null)"
sudo grep -q '^CREATE_PRIVATE_REPO_ON_PUSH: false' /opt/quay/quay-config/config.yaml 2>/dev/null && echo public=yes
echo "reg_trust=$(curl -s -m 8 -o /dev/null -w '%{http_code}' https://rhem.lab.internal:8443/health/instance 2>/dev/null)"
echo "reg_login=$(sudo podman login --get-login rhem.lab.internal:8443 2>/dev/null)"
[ -f ~/device/config.yaml ] && echo enroll_cfg=yes
grep -q 'server: https://rhem.lab.internal:7443' ~/device/config.yaml 2>/dev/null && echo enroll_server=yes
[ -f ~/device/registry-ca.pem ] && echo reg_ca_copy=yes
[ -f ~/device/Containerfile ] && echo containerfile=yes
grep -q 'rhel9/rhel-bootc' ~/device/Containerfile 2>/dev/null && echo cf_base=yes
grep -q 'flightctl-agent' ~/device/Containerfile 2>/dev/null && echo cf_agent=yes
grep -q 'useradd.*flightctl' ~/device/Containerfile 2>/dev/null && echo cf_useradd=yes
grep -q 'config.yaml /etc/flightctl' ~/device/Containerfile 2>/dev/null && echo cf_config=yes
grep -q 'ca-trust/source/anchors' ~/device/Containerfile 2>/dev/null && echo cf_ca=yes
echo "os_tags=$(sudo podman search --list-tags --format '{{.Tag}}' rhem.lab.internal:8443/admin/edge-os 2>/dev/null | tr '\n' ' ')"
echo "app_tags=$(sudo podman search --list-tags --format '{{.Tag}}' rhem.lab.internal:8443/admin/hello 2>/dev/null | tr '\n' ' ')"
[ -f ~/device/config.toml ] && echo bib_cfg=yes
grep -q 'key = "ssh-' ~/device/config.toml 2>/dev/null && echo bib_key=yes
sudo test -f ~/device/output/qcow2/disk.qcow2 && echo disk=yes
[ -f ~/fleet/lab-fleet.yaml ] && echo fleet_file=yes
grep -qP '\t' ~/fleet/lab-fleet.yaml 2>/dev/null && echo fleet_tabs=yes
python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" ~/fleet/lab-fleet.yaml >/dev/null 2>&1 && echo fleet_yaml=yes
echo "devices_json=$(flightctl get devices -o json 2>/dev/null | tr -d '\n')"
echo "fleet_json=$(flightctl get fleet/lab -o json 2>/dev/null | tr -d '\n')"
"""

_rhem = None


def rhem():
    global _rhem
    if _rhem is None:
        _rhem = facts("rhem", RHEM_FACTS)
        for key in ("devices_json", "fleet_json"):
            try:
                _rhem[key] = json.loads(_rhem.get(key) or "null")
            except ValueError:
                _rhem[key] = None
    return _rhem


def need_rhem(m):
    if rhem()["_reachable"]:
        return True
    m.skip("Could not log in to the rhem VM", "Finish the server-create exercise first.")
    return False


def devices():
    data = rhem().get("devices_json") or {}
    return data.get("items", []) if isinstance(data, dict) else []
