#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import requests
import json
from proxmoxer import ProxmoxAPI
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

requirements: [ "proxmoxer", "requests" ]

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
def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_host=dict(type='str', required=True),
            api_user=dict(type='str', required=True),
            api_password=dict(type='str', required=True, no_log=True),
            node=dict(type='str', required=True),
            storage=dict(type='str', required=True),
            verify_ssl=dict(type='bool', default=True),
            vmid=dict(type='int', default=None, required=False)
        )
    )
    storage = module.params['storage']
    node = module.params['node']
    vmid = module.params['vmid']
    proxmox = ProxmoxAPI(module.params['api_host'], user=module.params['api_user'], password=module.params['api_password'], verify_ssl=module.params['verify_ssl'])

    try:
        if storage == 'all':
            storages = [s['storage'] for s in proxmox.nodes(node).storage.get(content="backup")]
        else:
            storages = [storage]
        backups = []
        for stor in storages:
            backups.extend([backup for backup in proxmox.nodes(node).storage(stor).content.get(content='backup') if (vmid and vmid == backup['vmid']) or not vmid])
        backups.sort(key=lambda x: x['ctime'], reverse=True)
        module.exit_json(changed=False, latest=backups[0], backups=backups)

    except Exception as e:
        module.fail_json(msg=f"An unexpected error occurred: {str(e)}")

if __name__ == '__main__':
    main()