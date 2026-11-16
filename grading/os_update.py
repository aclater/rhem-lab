"""Grading for the os-update exercise: update and roll back the operating system."""
from .core import *  # noqa: F401,F403

NUM = 10
NAME = "os-update"
TITLE = "Update and roll back the operating system"


def grade():
    m = Exercise(NUM, NAME, TITLE)
    if not need_rhem(m):
        return m
    f = rhem()
    m.check("v2" in f.get("os_tags", "").split(), "edge-os:v2 is in the registry", "Build and push OS release v2 (step 1).")
    fleet = f.get("fleet_json") or {}
    spec = fleet.get("spec", {})
    seq = spec.get("rolloutPolicy", {}).get("deviceSelection", {}).get("sequence")
    m.check(seq, "The fleet has a staged rollout policy", "Add rolloutPolicy to lab-fleet.yaml, at the same level as selector (step 2).")
    want = spec.get("template", {}).get("spec", {}).get("os", {}).get("image", "")
    for d in devices():
        alias = d.get("metadata", {}).get("labels", {}).get("alias", "?")
        running = d.get("status", {}).get("os", {}).get("image", "")
        updated = d.get("status", {}).get("updated", {}).get("status", "?")
        m.check(running == want and updated == "UpToDate", f"{alias} runs the OS image the fleet names ({running.rsplit(':', 1)[-1] or '?'}, {updated})",
                f"The fleet names {want.rsplit(':', 1)[-1] or '?'}. A rollout may still be running: flightctl get devices")
    m.skip("Whether you went to v2 and back", "Not checked: the end state of this module is the same as its start.")
    return m
