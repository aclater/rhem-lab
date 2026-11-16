"""Grading for the workload-deploy exercise: deploy a workload."""
from .core import *  # noqa: F401,F403

NUM = 9
NAME = "workload-deploy"
TITLE = "Deploy a workload"


def grade():
    m = Exercise(NUM, NAME, TITLE)
    if not need_rhem(m):
        return m
    f = rhem()
    tags = f.get("app_tags", "").split()
    m.check("v1" in tags, f"hello:v1 is in the registry (tags: {' '.join(tags) or 'none'})", "Build and push it (step 1).")
    fleet = f.get("fleet_json") or {}
    apps = fleet.get("spec", {}).get("template", {}).get("spec", {}).get("applications") or []
    app = next((a for a in apps if a.get("name") == "hello"), None)
    if m.check(app, "The fleet deploys the application hello", "Add the applications section to lab-fleet.yaml and apply it (step 2)."):
        m.check(app.get("appType") == "container", "hello is a container application", "appType: container")
        m.check(app.get("runAs") == "flightctl", "hello runs as the flightctl user", "runAs: flightctl")
    for i, name in enumerate(EDGES, start=1):
        rc, out = run(["curl", "-s", "-m", "5", f"http://{SUBNET}.2{i}:8080/"])
        version = (re.search(r"Version: (\S+?)<", out) or [None, ""])[1]
        m.check("Hello from the edge" in out, f"{name} serves the application on port 8080" + (f" (version {version})" if version else ""),
                "Give a rollout two minutes. Then on the server: flightctl get devices")
    m.check("v2" in tags, "hello:v2 is in the registry", "Build and push version 2 (step 5).")
    m.check(app and str(app.get("image", "")).endswith(":v2"), "The fleet is on hello:v2", "Change the image tag in lab-fleet.yaml and apply it (step 5).")
    return m
