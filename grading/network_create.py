"""Grading for the network-create exercise: create the lab network."""
from .core import *  # noqa: F401,F403

NUM = 1
NAME = "network-create"
TITLE = "Create the lab network"


def grade():
    m = Exercise(NUM, NAME, TITLE)
    key = LAB / "keys/id_ed25519"
    m.check(key.exists() and key.with_suffix(".pub").exists(), "Lab SSH key exists (keys/id_ed25519)",
            "ssh-keygen -q -t ed25519 -N '' -C edgelab -f keys/id_ed25519")
    rc, xml = run(VIRSH + ["net-dumpxml", NET])
    if not m.check(rc == 0, f"Network {NET} is defined", "virsh -c qemu:///system net-define network.xml"):
        return m
    rc, info = run(VIRSH + ["net-info", NET])
    m.check(re.search(r"Active:\s+yes", info), f"Network {NET} is started", f"virsh -c qemu:///system net-start {NET}")
    m.check("lab.internal" in xml, "The network serves the domain lab.internal", "Define the network from the guide's network.xml.")
    hosts = set(re.findall(r"<host [^>]*name='([^']+)'", xml))
    want = {"rhem", *EDGES}
    m.check(want <= hosts, "Fixed addresses for rhem and edge-1 to edge-3",
            f"Missing in the network: {', '.join(sorted(want - hosts))}.")
    return m
