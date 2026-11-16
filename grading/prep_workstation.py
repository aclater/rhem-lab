"""Grading for the prep-workstation exercise: prepare the workstation."""
from .core import *  # noqa: F401,F403

NUM = 0
NAME = "prep-workstation"
TITLE = "Prepare the workstation"


def grade():
    m = Exercise(NUM, NAME, TITLE)
    rc, _ = run(VIRSH + ["list", "--all"])
    m.check(rc == 0, "You can manage system VMs (virsh -c qemu:///system)",
            "Install libvirt, start libvirtd, add yourself to the libvirt group, log out and in.")
    m.check(pathlib.Path("/dev/kvm").exists(), "KVM is available (/dev/kvm)", "Enable virtualization in the firmware.")
    m.check(shutil.which("virt-install"), "virt-install is installed", "sudo dnf install -y virt-install")
    home = pathlib.Path.home()
    _, acl = run(["getfacl", "-pc", str(home)])
    reachable = home.stat().st_mode & 0o001 or re.search(r"(?m)^user:qemu:..x", acl)
    m.check(reachable, "The VM service can pass through your home folder to the disk images",
            "chmod o+x ~")
    if not m.check(LAB.is_dir(), f"Working folder {LAB} exists", "mkdir ~/edgelab"):
        return m
    missing = [f for f in ("network.xml", "ssh_config") if not (LAB / f).is_file()]
    m.check(not missing, "Lab files copied into the working folder",
            f"Missing: {', '.join(missing)}. Run: cp guide/files/* .")
    if (LAB / "ssh_config").is_file():
        m.check("cloud-user" in (LAB / "ssh_config").read_text(), "ssh_config is the current version",
                "Yours is from an older version of the guide. Run: cp guide/files/ssh_config .")
    missing = [d for d in ("images", "keys", "inputs") if not (LAB / d).is_dir()]
    m.check(not missing, "Folders images, keys and inputs exist", f"Missing: {', '.join(missing)}. Run: mkdir {' '.join(missing)}")
    if (LAB / "keys").is_dir():
        m.check(mode(LAB / "keys") == "700", "keys is private (mode 700)", "chmod 700 keys")

    image = LAB / "inputs/rhel-9.8-x86_64-kvm.qcow2"
    if m.check(image.exists(), "inputs/rhel-9.8-x86_64-kvm.qcow2 is there",
               "Download the RHEL 9.8 KVM guest image and save it under exactly that name."):
        info = qemu_info(image)
        m.check(info.get("format") == "qcow2", "The RHEL image is a qcow2 disk image",
                "That file is not a qcow2 image. Download it again; a saved login page is a common cause.")

    offline = LAB / "offline"
    if offline.is_dir():
        missing = [f for f in OFFLINE_FILES if not (offline / f).is_file()]
        m.check(not missing, "offline holds the four files of a disconnected lab",
                f"Missing: {', '.join(missing)}. Appendix A, part 1, creates them; a classroom kit provides them.")

    act = LAB / "inputs/rhsm-activation"
    secret = LAB / "inputs/pull-secret.json"
    if offline.is_dir() and not act.exists() and not secret.exists():
        # Set up from a classroom kit: the files were prepared elsewhere and the server is never registered.
        m.skip("inputs/rhsm-activation and inputs/pull-secret.json",
               "Not needed: ~/edgelab/offline exists, so nothing is fetched from Red Hat.")
        return m
    if m.check(act.exists(), "inputs/rhsm-activation is there", "Create it with two lines: org=... and key=..."):
        lines = act.read_text().splitlines()
        good = len(lines) >= 2 and re.fullmatch(r"org=\S+", lines[0]) and re.fullmatch(r"key=\S+", lines[1])
        m.check(good, "rhsm-activation has org= on line 1 and key= on line 2",
                "Line 1 must be org=<organization ID>, line 2 key=<activation key>, with no spaces or quotes.")
        m.check(mode(act) == "600" or act.is_symlink(), "rhsm-activation is private (mode 600)", "chmod 600 inputs/rhsm-activation")

    if m.check(secret.exists(), "inputs/pull-secret.json is there", "Download your pull secret from console.redhat.com."):
        try:
            auths = json.loads(secret.read_text()).get("auths", {})
        except ValueError:
            auths = None
        m.check(auths is not None, "pull-secret.json is valid JSON", "The file is not JSON. Download it again.")
        if auths is not None:
            m.check("registry.redhat.io" in auths, "The pull secret has a login for registry.redhat.io",
                    "This pull secret has no registry.redhat.io entry.")
        m.check(mode(secret) == "600" or secret.is_symlink(), "pull-secret.json is private (mode 600)", "chmod 600 inputs/pull-secret.json")
    return m
