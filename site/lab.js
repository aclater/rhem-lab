// Page chrome for the lab guide: sidebar, terminal blocks with prompts, step numbers and checkboxes.
// Progress ticks are kept in this browser only (localStorage); the guide works without them.
const LAB_VERSION = "1.0.0";   // set by: make version V=x.y.z (keeps the VERSION file in step)

const EXERCISES = [
  { file: "index.html", num: "", name: "", title: "Overview" },
  { file: "00-prerequisites.html", num: "0", name: "prep-workstation", title: "Prepare the workstation" },
  { file: "01-network.html", num: "1", name: "network-create", title: "Create the lab network" },
  { file: "02-server-vm.html", num: "2", name: "server-create", title: "Create the server VM" },
  { file: "03-install-rhem.html", num: "3", name: "rhem-install", title: "Install Red Hat Edge Manager" },
  { file: "04-first-login.html", num: "4", name: "rhem-login", title: "Log in for the first time" },
  { file: "05-registry.html", num: "5", name: "registry-install", title: "Install a registry" },
  { file: "06-device-image.html", num: "6", name: "image-build", title: "Build the device image" },
  { file: "07-edge-vms.html", num: "7", name: "devices-enroll", title: "Create and enroll edge devices" },
  { file: "08-fleet.html", num: "8", name: "fleet-create", title: "Manage devices as a fleet" },
  { file: "09-workloads.html", num: "9", name: "workload-deploy", title: "Deploy a workload" },
  { file: "10-updates.html", num: "10", name: "os-update", title: "Update and roll back the operating system" },
  { file: "11-teardown.html", num: "11", name: "lab-teardown", title: "Remove the lab" },
  { file: "12-disconnected.html", num: "A", name: "disconnected", title: "Run the lab disconnected" },
  { file: "13-classroom.html", num: "B", name: "classroom", title: "Deliver the lab in a classroom" },
  { file: "14-iso-install.html", num: "C", name: "iso-install", title: "Install a device from an ISO" },
];
// Who you are and which machine you are on, for each kind of command block.
const HOSTS = {
  host: { user: "student", machine: "workstation", dir: "edgelab", label: "workstation" },
  rhem: { user: "cloud-user", machine: "rhem", dir: "~", label: "server VM" },
  prep: { user: "cloud-user", machine: "prep", dir: "~", label: "prep VM" },
  "edge-1": { user: "lab", machine: "edge-1", dir: "~", label: "device" },
  "edge-2": { user: "lab", machine: "edge-2", dir: "~", label: "device" },
  "edge-3": { user: "lab", machine: "edge-3", dir: "~", label: "device" },
  "edge-4": { user: "lab", machine: "edge-4", dir: "~", label: "device" },
};
const store = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* private window: carry on without progress */ } },
};
const last = location.pathname.split("/").pop();
// The overview may be served under another name; treat anything unknown as it.
const here = EXERCISES.some((m) => m.file === last) ? last : "index.html";
const escapeHtml = (t) => t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

function progress(file) {
  const total = Number(store.get(`steps:${file}`) || 0);
  if (!total) return "";
  let done = 0;
  for (let i = 0; i < total; i++) if (store.get(`done:${file}:${i}`) === "1") done++;
  return `<span class="prog${done === total ? " done" : ""}">${done === total ? "done" : `${done}/${total}`}</span>`;
}

function buildNav() {
  const nav = document.querySelector("nav.side");
  if (!nav) return;
  const items = EXERCISES.map((m) =>
    `<li><a class="${m.file === here ? "current" : ""}" href="${m.file}"><span class="num">${m.num}</span><span>${m.title}</span>${progress(m.file)}</a></li>`).join("");
  nav.innerHTML = `<p class="brand">Edge Manager lab</p><p class="sub">Red Hat Edge Manager 1.4 on RHEL 9</p>
    <ol>${items}</ol>
    <div class="legend"><b>The prompt shows where a command runs</b>
      <div><code>[student@workstation edgelab]$</code> your workstation</div>
      <div><code>[cloud-user@rhem ~]$</code> the server VM</div>
      <div><code>[lab@edge-1 ~]$</code> an edge device</div>
    </div>
    <p class="version">Lab guide version ${LAB_VERSION}</p>`;
}

// Turn each <pre class="cmd"> (and the <pre class="out"> that follows it, if any) into one terminal block:
// a prompt and the command in bold for every command line, then the expected output.
function buildTerminals() {
  const dirs = {};                                   // working folder per machine, followed across blocks
  const startDir = document.body.dataset.hostDir;    // a page may start outside the working folder
  document.querySelectorAll("pre.cmd").forEach((pre) => {
    const on = pre.dataset.on || "host";
    const host = HOSTS[on] || HOSTS.host;
    if (!(on in dirs)) dirs[on] = on === "host" && startDir ? startDir : host.dir;
    if (pre.dataset.dir) dirs[on] = pre.dataset.dir;    // a block may say which folder it starts in
    let user = host.user;
    const commands = pre.textContent.replace(/^\n+|\s+$/g, "");
    let html = "";
    let continued = false;                           // inside a here-document or after a trailing backslash
    let hereEnd = null;
    for (const line of commands.split("\n")) {
      if (continued) {
        html += `<span class="prompt">&gt; </span><b>${escapeHtml(line)}</b>\n`;
        if (hereEnd !== null) { if (line.trim() === hereEnd) { hereEnd = null; continued = false; } }
        else continued = /\\$/.test(line);
        continue;
      }
      html += `<span class="prompt">[${user}@${host.machine} ${dirs[on]}]$ </span><b>${escapeHtml(line)}</b>\n`;
      const doc = line.match(/<<-?\s*'?(\w+)'?\s*$/);
      if (doc) { hereEnd = doc[1]; continued = true; }
      else if (/\\$/.test(line)) continued = true;
      const cd = line.match(/^cd\s+(\S+)\s*$/);
      if (cd) dirs[on] = cd[1] === "~" ? "~" : cd[1].replace(/\/$/, "").split("/").pop();
      if (/^sudo -u flightctl -i$/.test(line)) user = "flightctl";
      else if (line === "exit" && user === "flightctl") user = host.user;
    }
    const next = pre.nextElementSibling;
    if (next && next.matches("pre.out")) {
      html += escapeHtml(next.textContent.replace(/^\n+|\s+$/g, "")) + "\n";
      next.remove();
    }
    const box = document.createElement("div");
    box.className = "term";
    box.dataset.on = on;
    box.innerHTML = `<div class="bar"><span class="where">${host.label}</span><button type="button">Copy</button></div><pre>${html}</pre>`;
    box.querySelector("button").addEventListener("click", async (e) => {
      try { await navigator.clipboard.writeText(commands + "\n"); e.target.textContent = "Copied"; }
      catch { e.target.textContent = "Select and copy"; }
      setTimeout(() => (e.target.textContent = "Copy"), 1400);
    });
    pre.replaceWith(box);
  });
}

function buildSteps() {
  const steps = document.querySelectorAll("section.step");
  store.set(`steps:${here}`, String(steps.length));
  steps.forEach((s, i) => {
    const h = s.querySelector("h2");
    const key = `done:${here}:${i}`;
    const box = document.createElement("input");
    box.type = "checkbox";
    box.id = `step-${i + 1}`;
    box.title = "Mark this step done";
    box.checked = store.get(key) === "1";
    s.classList.toggle("done", box.checked);
    box.addEventListener("change", () => {
      store.set(key, box.checked ? "1" : "0");
      s.classList.toggle("done", box.checked);
      buildNav();
    });
    const title = document.createElement("h3");
    title.className = "step-title";
    title.innerHTML = `<span class="step-num">${i + 1}.</span> <span>${h.innerHTML}</span>`;
    title.prepend(box);
    h.replaceWith(title);
  });
}

function buildPager() {
  const main = document.querySelector("main");
  const i = EXERCISES.findIndex((m) => m.file === here);
  if (!main || i < 0) return;
  const prev = EXERCISES[i - 1], next = EXERCISES[i + 1];
  const p = document.createElement("div");
  p.className = "pager";
  p.innerHTML = `<span>${prev ? `<a href="${prev.file}">← ${prev.title}</a>` : ""}</span>
    <span>${next ? `<a href="${next.file}">${next.title} →</a>` : ""}</span>`;
  main.appendChild(p);
}

buildTerminals();
buildSteps();
buildNav();
buildPager();
