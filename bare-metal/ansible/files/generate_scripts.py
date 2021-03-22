import os

NUM_OF_VMS = int(os.getenv('NUM_OF_VMS'))
BASE_NAME = os.getenv('BASE_NAME')
BASE_PATH = os.getenv('BASE_PATH')
RESTART_VM_FILE_NAME = os.getenv('RESTART_VM_FILE_NAME')


def generate_script():
    with open(f'files/{RESTART_VM_FILE_NAME}.sh', 'w') as f:
        f.write('#!/bin/bash\n')
        for i in range(1, NUM_OF_VMS+1):
            f.write(f'VBoxManage startvm {BASE_NAME}-{i} --type headless\n')


def generate_service_file():
    with open(f'files/{RESTART_VM_FILE_NAME}.service', 'w') as f:
        f.write(f'[Unit]\n' \
                + f'Description=Restart virtual mashines after host reboot\n\n' \
                + f'[Service]\n' \
                + f'Type=oneshot\n' \
                + f'RemainAfterExit=true\n' \
                + f'ExecStart={BASE_PATH}/{RESTART_VM_FILE_NAME}.sh\n\n' \
                + f'[Install]\n' \
                + f'WantedBy=multi-user.target\n' \
                )
        

if __name__ == "__main__":
    generate_script()
    generate_service_file()