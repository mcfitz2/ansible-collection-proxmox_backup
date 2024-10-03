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