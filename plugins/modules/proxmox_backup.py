#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import requests
import json
from proxmoxer import ProxmoxAPI
__metaclass__ = type

DOCUMENTATION = r'''
---
module: proxmox_backup_info

short_description: Get backup information from Proxmox.

version_added: "0.1.0"

description: Get backup information from Proxmox.

options:
    api_host:
        description: API Host.
        required: true
        type: str
    api_user:
        description: U
        required: true
        type: str
    specifications:
        description: Specification list.
        type: list
        elements: dict
        suboptions:
            negate:
                description: Negate flag.
                type: bool
            required:
                description: Required flag.
                type: bool
            name:
                description: Specification name.
                type: str
            implementation:
                description: Implementation.
                type: str
            fields:
                description: Configuration field list.
                type: list
                elements: dict
                suboptions:
                    name:
                        description: Field name.
                        type: str
                    value:
                        description: Field value.
                        type: raw

extends_documentation_fragment:
    - mcfitz2.proxmox

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
            vmid=dict(type='int', required=True),
            wait=dict(type='bool', default=False)
        )
    )
    storage = module.params['storage']
    node = module.params['node']
    vmid = module.params['vmid']
    wait = module.params['wait']
    proxmox = ProxmoxAPI(module.params['api_host'], user=module.params['api_user'], password=module.params['api_password'], verify_ssl=module.params['verify_ssl'])

    try:

        task_id = proxmox.nodes(node).vzdump.post(vmid=vmid, storage=storage)
        status = None
        if wait:
            status = proxmox.nodes(node).tasks(task_id).status.get()
            while status['status'] == 'running':
                status = proxmox.nodes(node).tasks(task_id).status.get()
                
        module.exit_json(changed=False, task_id=task_id, status=status)

    except Exception as e:
        module.fail_json(msg=f"An unexpected error occurred: {str(e)}")

if __name__ == '__main__':
    main()