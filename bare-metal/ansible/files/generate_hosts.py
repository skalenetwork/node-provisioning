import os

SUBNET = os.getenv('SUBNET')
NUM_OF_VMS = int(os.getenv('NUM_OF_VMS'))
BASE_IP = int(os.getenv('BASE_IP'))
SSH_USER = os.getenv('SSH_USER')

NODES_PREFIX = '[nodes]\n'

def generate_hosts():
    with open('hosts', 'w') as f:
        f.write(NODES_PREFIX)
        for i in range(1, NUM_OF_VMS+1):
            f.write(f'node{i} ansible_host={SUBNET}.{BASE_IP+i} ansible_ssh_user={SSH_USER}\n')

if __name__ == "__main__":
    generate_hosts()
