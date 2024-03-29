import os
import json

BASE_DIR = os.getenv('BASE_DIR')
INVENTORY_DIR = os.getenv('INVENTORY_DIR')
IPS_FILEPATH = os.path.join(BASE_DIR, 'node_ips.json')


def create_hosts_file_for_ansible():
    with open(f'{IPS_FILEPATH}') as f:
        nodes = json.load(f)
    first_string = '[nodes]'
    with open(f'{INVENTORY_DIR}/hosts', 'w') as hosts:
        hosts.write(first_string)

    for name, ip in nodes.items():
        host_string = f'{name} ansible_host={ip} ansible_user=ubuntu ansible_ssh_extra_args="-o StrictHostKeyChecking=no"'  # noqa
        with open(f'{INVENTORY_DIR}/hosts', 'a') as hosts:
            hosts.write('\n' + host_string)


def main():
    create_hosts_file_for_ansible()


if __name__ == "__main__":
    main()
