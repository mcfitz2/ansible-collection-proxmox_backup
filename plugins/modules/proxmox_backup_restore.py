#!/usr/bin/python
# Copyright: (c) 2020, Fuochi <devopsarr@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: proxmox_backup_restore

short_description: Restore a Proxmox LXC/VM from backup

version_added: "0.1.0"

description: Restore a Proxmox LXC/VM from backup

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
        default: 8006
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
        description: VMID of VM/LXC to restore
        type: int
        required: true
    backup:
        description: Backup to restore
        required: true
        type: str
    bandwidth_limit:
        description: Override I/O bandwidth limit (in KiB/s).
        type: int
        required: false
    storage:
        description: Destination datastore. If not specified, resource will be restored to its original datastore
        required: false
        type: str
    unique:
        description: Assign a unique random ethernet address.
        type: bool
        required: false
        default: false
    start_after_restore:
        description: Start VM/LXC after restore
        required: false
        default: false
        type: bool
    wait:
        description: If true, poll Proxmox until backup is complete/failed
        default: false
        required: false
        type: bool
    override:
        description: Override VM/LXC config from backup
        type: dict
        suboptions:
            unprivileged:
                description: Makes the container run as unprivileged user. Defaults to value in backup
                type: bool
            hostname:
                description: Override the VM/LXC hostname. Defaults to value in backup
                type: str
            memory:
                description: Override amount of memory (in MB) assigned to the VM/LXC. Defaults to value in backup
                type: int
            cores:
                description: Override number of cores assigned to the VM/LXC. Defaults to value in backup
                type: int

requirements: [ "proxmoxer" ]

author:
    - Micah Fitzgerald (@mcfitz2)
'''

EXAMPLES = r'''
---
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
task_id:
    description: UPID of restore task
    type: str
    returned: always
    sample: UPID
'''

from ansible.module_utils.basic import missing_required_lib  # noqa: E402
import traceback  # noqa: E402
from ansible.module_utils.basic import AnsibleModule  # noqa: E402
PROXMOXER_IMP_ERR = None
try:
    from proxmoxer import ProxmoxAPI
    from proxmoxer import ResourceException
    HAS_PROXMOXER = True
except ImportError:
    HAS_PROXMOXER = False
    PROXMOXER_IMP_ERR = traceback.format_exc()


def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_host=dict(type='str', required=True),
            api_user=dict(type='str', required=True),
            api_password=dict(type='str', required=True, no_log=True),
            api_port=dict(type='int', required=False, default=8006),
            node=dict(type='str', required=True),
            backup=dict(type='str', required=True),
            verify_ssl=dict(type='bool', default=True),
            vmid=dict(type='int', required=True),
            bandwidth_limit=dict(type='int', default=None, required=False),
            storage=dict(type='str', default=None, required=False),
            unique=dict(type='bool', default=False, required=False),
            start_after_restore=dict(type='bool', default=False),
            wait=dict(type='bool', default=False, required=False),
            override=dict(type="dict", options=dict(
                unprivileged=dict(type='bool', default=None),
                hostname=dict(type='str', default=None),
                memory=dict(type='int', default=None),
                cores=dict(type='int', default=None))
            )
        ),
        supports_check_mode=True
    )
    if not HAS_PROXMOXER:
        module.fail_json(msg=missing_required_lib(
            'proxmoxer'), exception=PROXMOXER_IMP_ERR)

    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    if module.check_mode:
        module.exit_json(**result)
    backup = module.params['backup']
    node = module.params['node']
    vmid = module.params['vmid']
    proxmox = ProxmoxAPI(module.params['api_host'],
                         user=module.params['api_user'],
                         password=module.params['api_password'],
                         verify_ssl=module.params['verify_ssl'])

    try:
        resource_type = None
        try:
            proxmox.nodes(node).lxc(vmid).get()
            resource_type = 'lxc'
        except ResourceException:
            try:
                proxmox.nodes(node).lxc(vmid).get()
                resource_type = 'qemu'
            except ResourceException as e:
                module.fail_json(msg=f"Unable to determine resource type: {str(e)}")
        if resource_type == 'lxc':
            upid = proxmox.nodes(node).lxc.post(vmid=vmid, ostemplate=backup, node=node, restore="1")
        elif resource_type == 'qemu':
            upid = proxmox.nodes(node).qemu.post(vmid=vmid, ostemplate=backup, node=node, restore="1")
        module.exit_json(changed=True, task_id=upid)

    except ResourceException as e:
        module.fail_json(msg=f"A Proxmox error occurred: {str(e)}")
    module.exit_json(changed=False)


if __name__ == '__main__':
    main()
