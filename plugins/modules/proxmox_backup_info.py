#!/usr/bin/python
# Copyright: (c) 2020, Fuochi <devopsarr@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: proxmox_backup_info

short_description: Get backup information from Proxmox.

version_added: "0.1.0"

description: Get backup information from Proxmox.

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
        required: true
        description:
        - Specify the password to authenticate with.
        - You can use E(PROXMOX_PASSWORD) environment variable.
        type: str
    verify_ssl:
        description:
        - If V(false), SSL certificates will not be validated.
        - This should only be used on personally controlled sites using self-signed certificates.
        type: bool
        default: true
    node:
        description: Proxmox node that you wish to query
        required: true
        type: str
    vmid:
        description: VMID of the VM/Container you wish to filter by
        required: false
        type: int
    storage:
        description: Storage identifier e.g. "local" or "all"
        choices: ['all', 'storage']
        required: false
        default: 'all'

requirements: [ "proxmoxer" ]

author:
    - Micah Fitzgerald (@mcfitz2)
'''

EXAMPLES = r'''
---
# Create a auto tag
- name: Get backups for VMID 701 accross all data stores
  mcfitz2.proxmox_backup:
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    vmid: 701
    node: pve-node
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
latest:
    description: Newest backup from results
    type: dict
    returned: always
backups:
    description: List of backups
    returned: always
    type: list
'''

from ansible.module_utils.basic import missing_required_lib
import traceback
from ansible.module_utils.basic import AnsibleModule
PROXMOXER_IMP_ERR = None
try:
    from proxmoxer import ProxmoxAPI
    from proxmoxer import ResourceException
    HAS_PROXMOXER = True
except ImportError:
    HAS_PROXMOXER = False
    PROXMOXER_IMP_ERR = traceback.format_exc()


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            api_host=dict(type='str', required=True),
            api_user=dict(type='str', required=True),
            api_password=dict(type='str', required=True, no_log=True),
            api_port=dict(type='int', required=False, default=8006),
            node=dict(type='str', required=True),
            storage=dict(type='str', required=False, default='all'),
            verify_ssl=dict(type='bool', default=True),
            vmid=dict(type='int', default=None, required=False)
        )
    )
    if not HAS_PROXMOXER:
        module.fail_json(msg=missing_required_lib(
            'proxmoxer'), exception=PROXMOXER_IMP_ERR)
    storage = module.params['storage']
    node = module.params['node']
    vmid = module.params['vmid']
    proxmox = ProxmoxAPI(module.params['api_host'],
                         user=module.params['api_user'],
                         password=module.params['api_password'],
                         verify_ssl=module.params['verify_ssl'])

    try:
        if storage == 'all':
            storages = [s['storage']
                        for s in proxmox.nodes(node).storage.get(content="backup")]
        else:
            storages = [storage]
        backups = []
        for stor in storages:
            backups.extend([backup
                            for backup in
                            proxmox.nodes(node).storage(
                                stor).content.get(content='backup')
                            if (vmid and vmid == backup['vmid']) or not vmid])
        backups.sort(key=lambda x: x['ctime'], reverse=True)
        module.exit_json(changed=False, latest=backups[0], backups=backups)

    except ResourceException as e:
        module.fail_json(msg=f"A Proxmox error occurred: {str(e)}")


def main():
    run_module()


if __name__ == '__main__':
    main()
