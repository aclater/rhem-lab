"""Grading for the image-build exercise: build the device image."""
from .core import *  # noqa: F401,F403

NUM = 6
NAME = "image-build"
TITLE = "Build the device image"


def grade():
    m = Exercise(NUM, NAME, TITLE)
    if not need_rhem(m):
        return m
    f = rhem()
    if m.check(f.get("enroll_cfg"), "~/device/config.yaml (enrollment configuration) exists", "Run the flightctl certificate request command (step 1)."):
        m.check(f.get("enroll_server"), "It points devices at https://rhem.lab.internal:7443",
                "The file is empty or wrong. Log in with flightctl and request the certificate again.")
    m.check(f.get("reg_ca_copy"), "~/device/registry-ca.pem exists", "In ~/device: sudo cat /opt/quay/quay-rootCA/rootCA.pem > registry-ca.pem")
    if m.check(f.get("containerfile"), "~/device/Containerfile exists", "Write it (step 3)."):
        m.check(f.get("cf_base"), "Containerfile starts from rhel9/rhel-bootc", "FROM registry.redhat.io/rhel9/rhel-bootc:9.8")
        m.check(f.get("cf_agent"), "Containerfile installs flightctl-agent", "Add the dnf install flightctl-agent step.")
        m.check(f.get("cf_config"), "Containerfile adds config.yaml to /etc/flightctl", "ADD config.yaml /etc/flightctl/config.yaml")
        m.check(f.get("cf_ca"), "Containerfile adds the registry CA to the trust anchors", "ADD registry-ca.pem /etc/pki/ca-trust/source/anchors/lab-registry-ca.pem")
        m.check(not f.get("cf_useradd"), "Containerfile does not create the flightctl user itself",
                "Remove the useradd line: the 1.4 agent package creates the user, and the build fails with it.")
    m.check("v1" in f.get("os_tags", "").split(), f"edge-os:v1 is in the registry (tags: {f.get('os_tags', '').strip() or 'none'})",
            "Build and push it (step 4).")
    if m.check(f.get("bib_cfg"), "~/device/config.toml exists", "Write it (step 5)."):
        m.check(f.get("bib_key"), "config.toml holds your lab public key",
                "The key line must be the key itself (ssh-ed25519 AAAA...), not LAB_PUBLIC_KEY. Run the sed command in step 5, "
                "then build the disk again.")
    m.check(f.get("disk"), "The disk image was built (~/device/output/qcow2/disk.qcow2)", "Run bootc-image-builder (step 5).")
    local = LAB / "images/edge-os-v1.qcow2"
    m.check(local.exists() and qemu_info(local).get("format") == "qcow2", "images/edge-os-v1.qcow2 is on the workstation",
            "scp -F ~/edgelab/ssh_config rhem:device/output/qcow2/disk.qcow2 images/edge-os-v1.qcow2")
    return m
