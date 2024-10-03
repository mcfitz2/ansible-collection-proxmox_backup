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
    storage:
        description: Data store that holds the desired backup
        required: true
        type: str
    vmid:
        description: VMID of VM/LXC to restore
        type: int
        required: true

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

from ansible.module_utils.basic import missing_required_lib  # noqa: E402
import traceback  # noqa: E402
from ansible.module_utils.basic import AnsibleModule  # noqa: E402
PROXMOXER_IMP_ERR = None
try:
    # from proxmoxer import ProxmoxAPI
    # from proxmoxer import ResourceException
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
            storage=dict(type='str', required=True),
            verify_ssl=dict(type='bool', default=True),
            vmid=dict(type='int', required=True)
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
    # storage = module.params['storage']
    # node = module.params['node']
    # vmid = module.params['vmid']
    # proxmox = ProxmoxAPI(module.params['api_host'],
    #                      user=module.params['api_user'],
    #                      password=module.params['api_password'],
    #                      verify_ssl=module.params['verify_ssl'])

    # try:
    #     module.exit_json(changed=False)

    # except ResourceException as e:
    #     module.fail_json(msg=f"A Proxmox error occurred: {str(e)}")
    module.exit_json(changed=False)


if __name__ == '__main__':
    main()
