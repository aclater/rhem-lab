# Edge Manager lab

A hands-on lab: deploy Red Hat Edge Manager 1.4 on a RHEL 9 virtual machine, build a RHEL image mode device image,
enroll three edge VMs, and manage them as a fleet with a workload and an operating system update.

You run every step yourself, on one Linux workstation with KVM. The guide explains what each step does, why, and
what it changes in the result.

## Read the guide

```
make serve     # starts the guide in the background and prints its address
make stop      # stops it
```

Start with "Prepare the workstation". Appendix A covers running the whole lab with no internet access. Appendix B is for instructors: it packs the lab
into one kit for a classroom of disconnected workstations.

## Check your work

The guide sets up a `lab` command in your working folder:

```
./lab status             # where you are, and the next thing to do
./lab start EXERCISE     # before an exercise
./lab grade EXERCISE     # after it: each check passes or fails, with a hint
./lab finish EXERCISE    # close it and move on
```

It only reads; it never changes anything.

## What is in this repository

| Path | Contents |
|---|---|
| `site/` | The guide: plain HTML, no build step, no external assets |
| `files/` | The files the guide copies into the working folder: the lab network definitions (connected and disconnected) and SSH settings |
| `ansible/` | Optional playbooks: the disconnected setup of Appendix A, and the classroom kit of Appendix B |
| `lab`, `grading/` | The `lab` command and one grading script per exercise |
| `serve.py` | The local web server behind `make serve` |
| `DECISIONS.md` | Design decisions and the reasons for them |

## Requirements

A workstation running RHEL 9, RHEL 10 or Fedora with KVM, and a Red Hat subscription that includes Red Hat Edge
Manager. The guide lists the memory, disk space and packages needed; every package is in the standard RHEL
repositories.
