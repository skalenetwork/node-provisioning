import os

NUM_OF_VMS = int(os.getenv('NUM_OF_VMS'))
BASE_NAME = os.getenv('BASE_NAME')
BASE_PATH = os.getenv('BASE_PATH')


def generate_script():
    with open(f'files/restart_vm.sh', 'w') as f:
        f.write('#!/bin/bash\n')
        for i in range(1, NUM_OF_VMS+1):
            f.write(f'VBoxManage startvm {BASE_NAME}-{i} --type headless\n')
        

if __name__ == "__main__":
    generate_script()