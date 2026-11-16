"""Grading scripts, one module per exercise, in guide order."""
from . import (prep_workstation, network_create, server_create, rhem_install, rhem_login, registry_install, image_build, devices_enroll, fleet_create, workload_deploy, os_update, lab_teardown)

EXERCISES = [prep_workstation, network_create, server_create, rhem_install, rhem_login, registry_install, image_build, devices_enroll, fleet_create, workload_deploy, os_update, lab_teardown]
