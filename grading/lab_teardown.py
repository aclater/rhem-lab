"""Grading for the lab-teardown exercise: remove the lab."""
from .core import *  # noqa: F401,F403

NUM = 11
NAME = "lab-teardown"
TITLE = "Remove the lab"


def grade():
    m = Exercise(NUM, NAME, TITLE)
    for name in ["rhem", *EDGES]:
        m.check(not vm_state(name), f"VM {name} is removed",
                f"virsh -c qemu:///system destroy {name}; virsh -c qemu:///system undefine {name} --nvram")
    rc, _ = run(VIRSH + ["net-info", NET])
    m.check(rc != 0, f"Network {NET} is removed", f"virsh -c qemu:///system net-destroy {NET}; virsh -c qemu:///system net-undefine {NET}")
    m.skip("The server's Red Hat registration", "Not checked: it cannot be seen once the VM is gone. Unregister before deleting the VM.")
    m.skip("The working folder", "Not checked: this command lives in it. Delete ~/edgelab last.")
    return m
