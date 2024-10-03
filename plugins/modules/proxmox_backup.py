#!/usr/bin/python
# Copyright: (c) 2020, Fuochi <devopsarr@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: proxmox_backup

short_description: Trigger a backup on Proxmox

version_added: "0.1.0"

description: Trigger a backup on Proxmox

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
    node:
        description: Proxmox node that you wish to query
        required: true
        type: str

requirements: [ "proxmoxer" ]

author:
    - Micah Fitzgerald (@mcfitz2)
'''

EXAMPLES = r'''
---
# Create a auto tag
- name: Create a auto tag
  devopsarr.sonarr.sonarr_auto_tag:
    remove_tags_automatically: false
    name: "Type"
    tags: [1]
    specifications:
    - name: "anime"
      implementation: "SeriesTypeSpecification"
      negate: false
      required: true
      fields:
      - name: "value"
        value: 2

# Delete a auto tag
- name: Delete a auto tag
  devopsarr.sonarr.sonarr_auto_tag:
    name: Example
    state: absent
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
id:
    description: auto tagID.
    type: int
    returned: always
    sample: 1
name:
    description: Name.
    returned: always
    type: str
    sample: "Example"
remove_tags_automatically:
    description: Remove tags automatically flag.
    returned: always
    type: bool
    sample: false
specifications:
    description: specification list.
    type: list
    returned: always
tags:
    description: Tag list.
    type: list
    returned: always
    elements: int
    sample: [1,2]
'''

from ansible.module_utils.basic import AnsibleModule
import traceback

PROXMOXER_IMP_ERR = None
try:
    from proxmoxer import ProxmoxAPI
    from proxmoxer import ResourceException
    from proxmoxer import __version__ as proxmoxer_version
    HAS_PROXMOXER = True
except ImportError:
    HAS_PROXMOXER = False
    PROXMOXER_IMP_ERR = traceback.format_exc()

from ansible.module_utils.basic import missing_required_lib
def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_host=dict(type='str', required=True),
            api_user=dict(type='str', required=True),
            api_password=dict(type='str', required=True, no_log=True),
            node=dict(type='str', required=True),
            storage=dict(type='str', required=True),
            verify_ssl=dict(type='bool', default=True),
            vmid=dict(type='int', required=True),
            wait=dict(type='bool', default=False)
        )
    )
    if not HAS_PROXMOXER:
        module.fail_json(msg=missing_required_lib('proxmoxer'), exception=PROXMOXER_IMP_ERR)
    storage = module.params['storage']
    node = module.params['node']
    vmid = module.params['vmid']
    wait = module.params['wait']
    proxmox = ProxmoxAPI(module.params['api_host'],
                         user=module.params['api_user'],
                         password=module.params['api_password'],
                         verify_ssl=module.params['verify_ssl'])

    try:

        task_id = proxmox.nodes(node).vzdump.post(vmid=vmid, storage=storage)
        status = None
        if wait:
            status = proxmox.nodes(node).tasks(task_id).status.get()
            while status['status'] == 'running':
                status = proxmox.nodes(node).tasks(task_id).status.get()
        module.exit_json(changed=False, task_id=task_id, status=status)

    except ResourceException as e:
        module.fail_json(msg=f"A Proxmox error occurred: {str(e)}")

if __name__ == '__main__':
    main()
