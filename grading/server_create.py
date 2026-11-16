"""Grading for the server-create exercise: create the server vm."""
from .core import *  # noqa: F401,F403

NUM = 2
NAME = "server-create"
TITLE = "Create the server VM"


def grade():
    m = Exercise(NUM, NAME, TITLE)
    disk = LAB / "images/rhem.qcow2"
    if m.check(disk.exists(), "images/rhem.qcow2 exists", "cp --sparse=always inputs/rhel-9.8-x86_64-kvm.qcow2 images/rhem.qcow2"):
        size = qemu_info(disk).get("virtual-size", 0) / 2**30
        m.check(size >= 79, f"The server disk is 80 GiB (found {size:.0f} GiB)", "qemu-img resize images/rhem.qcow2 80G  (before the first boot)")

    state = vm_state("rhem")
    if not m.check(state, "VM rhem exists", "Create it with the virt-install command in step 2."):
        return m
    if not m.check(state == "running", "VM rhem is running", "virsh -c qemu:///system start rhem"):
        return m
    f = facts("rhem", 'echo "hostname=$(hostname -f)"\necho "rootgb=$(df -BG --output=size / | tail -1 | tr -dc 0-9)"\nsudo -n true 2>/dev/null && echo sudo=yes\n')
    if not m.check(f["_reachable"], "You can log in: ssh -F ~/edgelab/ssh_config rhem",
                   "Wait a minute after starting it. If it never works: was --cloud-init clouduser-ssh-key=keys/id_ed25519.pub "
                   "on the virt-install command? Delete the VM, recreate images/rhem.qcow2 and create it again."):
        return m
    m.check(f.get("hostname") == "rhem.lab.internal", f"The server calls itself rhem.lab.internal (found {f.get('hostname', '?')})",
            "The name comes from the lab network. Was the MAC address 52:54:00:a0:00:10? Restarting the VM once also fixes a first-boot miss.")
    m.check(int(f.get("rootgb") or 0) >= 70, f"The root filesystem filled the disk ({f.get('rootgb', '?')} GB)",
            "The disk was not resized to 80G before the first boot.")
    m.check(f.get("sudo") == "yes", "cloud-user can use sudo without a password", "Was the VM made from the RHEL KVM guest image?")
    rc, xml = run(VIRSH + ["dumpxml", VM_PREFIX + "rhem"])
    m.check("cloudinit.iso" not in xml, "The VM has been restarted once since it was created",
            "virsh -c qemu:///system shutdown rhem, wait for 'shut off', then virsh -c qemu:///system start rhem (step 4).")
    return m
