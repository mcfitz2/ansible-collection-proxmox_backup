# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    # Common parameters for Proxmox VE modules
    DOCUMENTATION = r'''
options:
  api_host:
    description:
      - Specify the target host of the Proxmox VE cluster.
    type: str
    required: true
  api_port:
    description:
      - Specify the target port of the Proxmox VE cluster.
      - Uses the E(PROXMOX_PORT) environment variable if not specified.
    type: int
    required: false
    version_added: 9.1.0
  api_user:
    description:
      - Specify the user to authenticate with.
    type: str
    required: true
  api_password:
    description:
      - Specify the password to authenticate with.
      - You can use E(PROXMOX_PASSWORD) environment variable.
    type: str
  verify_ssl:
    description:
      - If V(false), SSL certificates will not be validated.
      - This should only be used on personally controlled sites using self-signed certificates.
    type: bool
    default: false
requirements: [ "proxmoxer", "requests" ]
'''