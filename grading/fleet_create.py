"""Grading for the fleet-create exercise: manage devices as a fleet."""
from .core import *  # noqa: F401,F403

NUM = 8
NAME = "fleet-create"
TITLE = "Manage devices as a fleet"


def grade():
    m = Exercise(NUM, NAME, TITLE)
    if not need_rhem(m):
        return m
    f = rhem()
    if m.check(f.get("fleet_file"), "~/fleet/lab-fleet.yaml exists", "Write it (step 1)."):
        m.check(not f.get("fleet_tabs"), "lab-fleet.yaml is indented with spaces, not tabs", "Replace the tabs with spaces, two per level.")
        m.check(f.get("fleet_yaml"), "lab-fleet.yaml is valid YAML",
                "python3 -c \"import yaml,sys; yaml.safe_load(open(sys.argv[1]))\" ~/fleet/lab-fleet.yaml  shows the line.")
    fleet = f.get("fleet_json")
    if not m.check(fleet, "Fleet lab exists in Edge Manager", "flightctl apply -f ~/fleet/lab-fleet.yaml"):
        return m
    sel = fleet.get("spec", {}).get("selector", {}).get("matchLabels", {})
    m.check(sel == {"site": "lab"}, f"The fleet selects site=lab (found {sel})", "selector.matchLabels must be site: lab")
    image = fleet.get("spec", {}).get("template", {}).get("spec", {}).get("os", {}).get("image", "")
    m.check(image.startswith(f"{REGISTRY}/admin/edge-os:"), f"The fleet pins the OS image ({image or 'none'})",
            "template.spec.os.image is missing or indented under the wrong key.")
    owned = [d for d in devices() if d.get("metadata", {}).get("owner") == "Fleet/lab"]
    m.check(len(owned) >= 3, f"All three devices are owned by the fleet (found {len(owned)})", "Devices need the label site=lab.")
    return m
