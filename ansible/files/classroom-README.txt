Edge Manager lab: classroom kit

This folder holds everything the lab needs. Nothing is downloaded.

  guide/      the lab guide, the lab command and the playbooks
  inputs/     the RHEL 9.8 guest image
  offline/    Edge Manager's packages and images, the registry installer and the base images
  SHA256SUMS  checksums of the files in inputs/ and offline/

To set up this workstation, open a terminal in this folder and run:

  ansible-playbook guide/ansible/classroom-student.yml

It checks the workstation, checks the files, and creates the working folder ~/edgelab.
Then read the guide:

  cd ~/edgelab
  make -C guide serve

Open the address it prints and start at "Run the lab disconnected", part 2.
