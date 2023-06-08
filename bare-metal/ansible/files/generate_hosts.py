import os

SUBNET = os.getenv('SUBNET')
NUM_OF_VMS = int(os.getenv('NUM_OF_VMS'))
BASE_IP = int(os.getenv('BASE_IP'))
SSH_USER = os.getenv('SSH_USER')
BASE_NAME = os.getenv('VM_BASE_NAME')

NODES_PREFIX = '[nodes]\n'


def generate_hosts():
    with open('hosts', 'w') as f:
        f.write(NODES_PREFIX)
        for i in range(0, NUM_OF_VMS):
            line = f'{BASE_NAME}-{i} ansible_host={SUBNET}.{BASE_IP+i} ansible_ssh_user={SSH_USER}\n'  # noqa
            f.write(line)


if __name__ == "__main__":
    generate_hosts()
