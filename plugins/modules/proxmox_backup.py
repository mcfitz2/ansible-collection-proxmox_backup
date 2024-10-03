#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import requests
import json
from proxmoxer import ProxmoxAPI

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