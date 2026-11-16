# Design decisions

Each entry gives the decision, the reason, the alternatives considered and the trade-off accepted.

## RHEL 9.8 for the server and the devices

- **Decision:** the lab uses RHEL 9.8 throughout.
- **Why:** Red Hat Edge Manager 1.4 supports RHEL 9 and 10, but the Red Hat Device Edge 4 compatibility matrix lists
  RHEL 9.8 with MicroShift 4.22 as fully supported and RHEL 10.2 as Technology Preview. Devices built here can take
  MicroShift later on a supported base.
- **Alternatives:** RHEL 10.2, or both.
- **Trade-off:** readers on RHEL 10 adapt repository names and the `rhel-bootc` and `bootc-image-builder` images.

## Edge Manager standalone on RHEL

- **Decision:** Edge Manager runs on a single RHEL VM as podman containers under systemd.
- **Why:** it is the smallest footprint, and every part of the server is visible as an ordinary systemd unit.
- **Alternatives:** Edge Manager on OpenShift.
- **Trade-off:** no high availability; the lab does not cover the OpenShift installation.

## The mirror registry as the lab registry, with public repositories

- **Decision:** device and application images live in Red Hat's mirror registry on the server VM, and repositories
  are public on the lab network.
- **Why:** devices pull their own images, so the registry is part of the deployment; public repositories mean a
  device only has to trust the registry, and no pull secret is built into device images.
- **Alternatives:** private repositories with pull secrets on devices.
- **Trade-off:** acceptable only because the registry is reachable from the lab network alone.

## Early binding

- **Decision:** the enrollment configuration is built into the device image.
- **Why:** a device enrolls by itself at first boot, with nothing injected at provisioning time.
- **Alternatives:** late binding, where the configuration is supplied when a device is provisioned.
- **Trade-off:** the image is tied to one Edge Manager installation and must stay in a registry you control.

## VMs created with virt-install

- **Decision:** every VM is created with `virt-install`.
- **Why:** it is the standard tool, it ships in RHEL AppStream, and every setting is a visible option.
- **Alternatives:** hand-written libvirt XML with `virsh define`.
- **Trade-off:** the server VM is restarted once after creation, because `virt-install` powers a cloud-init VM off
  at its first reboot.

## Literal commands

- **Decision:** steps do not depend on the reader recognising a variable, a placeholder or a shell substitution.
  Files shown in the guide are literal. Commands do not rely on a variable from an earlier step. Commands are the
  plain form an administrator would use: full output read or paged, files changed in an editor.
- **Why:** readers type as well as paste, and a step has to work either way.
- **Exceptions:** registering the server needs the reader's own organization ID and activation key; three commands
  keep a `$( )` substitution and say what it does.
- **Trade-off:** the server's login user is the image's built-in `cloud-user`.

## One fixed lab password

- **Decision:** the two accounts the lab creates (Edge Manager `admin`, registry `admin`) use the password
  `edgelab123`, shown in the guide and entered on the command line.
- **Why:** the lab exists only on the reader's workstation, and a known password keeps every reader's commands and
  output identical to the guide.
- **Alternatives:** prompting for a password of the reader's choice.
- **Trade-off:** not a pattern for real systems; the guide says so. The reader's own Red Hat credentials are
  handled separately, as files that are never copied into the repository.

## Workstation packages from RHEL repositories only

- **Decision:** every prerequisite is an RPM in RHEL BaseOS or AppStream.
- **Checked on:** RHEL 9.8 and RHEL 10.2. The repository's scripts run on Python 3.9 and later.

## A lab command for checking work

- **Decision:** a `lab` command with `start`, `grade` and `finish` per named exercise, plus `status` and `list`;
  one grading script per exercise in `grading/`; standard-library Python; read-only.
- **Why:** a reader can confirm each exercise before building on it, and the checks test correctness rather than
  the existence of files. Nothing has to be installed to run it.
- **Alternatives:** a general-purpose test tool, which would add a dependency that is not in the RHEL repositories.
- **Trade-off:** `start` only verifies earlier exercises and `finish` only confirms completion, because each
  exercise builds on the previous one and there is nothing to provision or clean up between them.

## Page layout

- **Decision:** every page is a guided exercise with the same sections: Outcomes, Before you begin, Instructions
  (numbered steps), Evaluation and Finish. Commands are shown as terminal blocks with the prompt of the machine they
  run on, the command in bold and the expected output beneath; long output is cut with `...output omitted...`.
  Notes use three kinds only: Note, Important, Warning.
- **Why:** a fixed layout lets a reader find the same thing in the same place on every page, and the prompt says
  where a command runs without a separate label.
- **Trade-off:** the pages are plain HTML, and the terminal blocks are assembled in the browser by `site/lab.js`.

## Disconnected appendix

- **Decision:** the appendix follows Red Hat's offline bundle path (`flightctl-mirror-images` with RPMs), prepared in
  a temporary registered RHEL 9 VM, and runs the lab on a libvirt network with no forwarding.
- **Why:** it is the documented path for a single server, and one archive carries both the images and the RPMs.
- **What the appendix adds to the documented procedure,** each found by running it on RHEL 9.8 with Edge Manager
  1.4.0: install the bundle's RPMs before anything else (a fresh guest image has no podman or skopeo); run the local
  registry and the import as root; redirect `registry.access.redhat.com` as well; read image signatures from the
  local store; fetch the gateway's nginx image separately, because the bundle omits it; give the network a default
  route, because the first start needs one to find the server's address.
- **Alternatives:** an offline RPM repository mirrored with subscription tooling plus a private registry.
- **Trade-off:** signature checking stays on, at the cost of two small configuration edits.

## Playbooks for the disconnected setup

- **Decision:** two Ansible playbooks in `ansible/` do the setup of Appendix A: one gathers the offline files, one
  builds the disconnected network and a server ready for Edge Manager. They are an optional resource; the appendix
  still gives every step by hand.
- **Why:** the offline files are prepared once and reused, and the server plumbing is repetitive; someone preparing
  a class needs the result, not the practice.
- **Alternatives:** a shell script; automating the whole lab.
- **Trade-off:** `ansible-core` becomes a prerequisite for this resource only. The playbooks use built-in modules
  alone, so no collection is needed, and they stop before Edge Manager is configured, where the learning starts.

## A classroom kit, set up per workstation

- **Decision:** for a class, the instructor builds one folder holding the guide, the guest image and the offline
  files; each student sets up their own workstation from it with one playbook and then does the disconnected lab by
  hand. The kit holds no Red Hat account details.
- **Why:** students need no account and no network, every workstation ends in the state module 0 produces, and the
  kit travels on media or as one file.
- **Alternatives:** the instructor configuring every workstation over SSH from an inventory; one shared host
  running every student's VMs; carrying the workstation packages in the kit.
- **Trade-off:** workstation packages are installed in advance, because they must match each workstation's own
  release; `ansible-core` is a prerequisite on student workstations.


## Setting up workstations from the instructor's

- **Decision:** a third classroom playbook, `classroom-push.yml`, copies the kit to a list of student workstations
  over SSH and runs the same setup there. It is an option next to the student-run playbook, which stays the default.
- **Why:** in a room where the instructor can already log in to the workstations, one command prepares all of them,
  and students need neither `ansible-core` nor the setup step.
- **Alternatives:** only the student-run playbook; installing the workstation packages from the instructor's
  workstation as well.
- **Trade-off:** it needs SSH access and a list of workstations, and it still does nothing as root, so packages and
  the `libvirt` group remain a prerequisite.

## An installer ISO as an appendix

- **Decision:** Appendix C builds an unattended installer ISO from the device image with bootc-image-builder and a
  kickstart file, and installs a fourth device from it. The main path keeps the disk image.
- **Why:** physical devices are usually installed from boot media, and the ISO shows what changes: the login user
  and the disk layout move from the image builder's settings to the kickstart file. A disk image is faster and
  needs less memory, so it stays the route for the three lab devices.
- **Alternatives:** an ISO for all devices; a network (PXE) install.
- **Trade-off:** the ISO build downloads installer packages with the server's registration, so the appendix does
  not work in the disconnected lab.

## A version number for the guide

- **Decision:** the guide carries one version number, `major.minor.patch`, in the file `VERSION`. Every page shows
  it at the bottom of the sidebar, `./lab version` prints it, and each version is a `v` tag in git.
  `make version V=1.2.3` sets the file and the sidebar together. Major: an existing working folder no longer
  matches the guide. Minor: new or reworked exercises. Patch: corrections.
- **Why:** copies of the guide travel without git history, in the classroom kit and on the hosted page, and a
  student, an instructor and a problem report need to name the same copy.
- **Alternatives:** the git commit alone, which a kit copy does not have; a build date, which says nothing about
  compatibility.
- **Trade-off:** the number lives in two files, `VERSION` and `site/lab.js`, because the pages must also work
  opened from disk. `./lab version` fails when they differ.
