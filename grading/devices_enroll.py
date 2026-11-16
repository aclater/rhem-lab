"""Grading for the devices-enroll exercise: create and enroll edge devices."""
from .core import *  # noqa: F401,F403

NUM = 7
NAME = "devices-enroll"
TITLE = "Create and enroll edge devices"


def grade():
    m = Exercise(NUM, NAME, TITLE)
    for name in EDGES:
        disk = LAB / f"images/{name}.qcow2"
        if m.check(disk.exists(), f"images/{name}.qcow2 exists", f"cp --sparse=always images/edge-os-v1.qcow2 images/{name}.qcow2"):
            state = vm_state(name)
            m.check(state == "running", f"VM {name} is running" if state else f"VM {name} exists",
                    f"virsh -c qemu:///system start {name}" if state else f"Create it with the virt-install command for {name} in step 1.")
    if not need_rhem(m):
        return m
    by_alias = {d.get("metadata", {}).get("labels", {}).get("alias"): d for d in devices()}
    m.check(len(devices()) >= 3, f"Three devices are enrolled (found {len(devices())})",
            "On the server: flightctl get enrollmentrequests, then approve them (step 3).")
    for name in EDGES:
        d = by_alias.get(name)
        if not m.check(d, f"A device is labelled alias={name}", "The agent proposes alias from the hostname; was the VM created with the MAC address for this name?"):
            continue
        m.check(d["metadata"]["labels"].get("site") == "lab", f"{name} is labelled site=lab", "It was approved without -l site=lab.")
        status = d.get("status", {}).get("summary", {}).get("status", "?")
        m.check(status == "Online", f"{name} is Online (reported: {status})", "Is the VM running? Give it a minute after boot.")
    return m
