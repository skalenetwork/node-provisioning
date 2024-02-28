import os
import ipaddress


NUM_OF_VMS = int(os.getenv('NUM_OF_VMS'))
BASE_IP = os.getenv('BASE_IP')
SSH_USER = os.getenv('SSH_USER')
BASE_NAME = os.getenv('VM_BASE_NAME')
HOSTS_FILEPATH = os.getenv('HOSTS_FILEPATH', 'hosts')


def get_line(index, base_ip=BASE_IP, base_name=BASE_NAME):
    ip = ipaddress.ip_address(BASE_IP) + index
    return f'{BASE_NAME}-{index} ansible_host={ip}'  # noqa


def generate_hosts(number, add_sgx, add_archive, add_geth):
    nodes_number = number
    if add_archive:
        nodes_number -= 1
    if add_geth:
        nodes_number -= 1
    hosts = {
        'nodes': [get_line(i) for i in range(0, nodes_number)]
    }
    if add_sgx:
        hosts.update({
            'sgx': [get_line(i) for i in range(0, nodes_number)]
        })
    if add_archive:
        hosts.update({'archive': [get_line(number - 2)]})
    if add_geth:
        hosts.update({'geth': [get_line(number - 1)]})

    lines = []
    for i, (k, v) in enumerate(hosts.items()):
        lines.extend((f'[{k}]', *v))
        if i < len(hosts) - 1:
            lines.append('\n')
    return '\n'.join(map(str, lines))


def save(hosts, filepath):
    with open(filepath, 'w') as f:
        f.write(hosts)


def main():
    if NUM_OF_VMS > 3:
        hosts = generate_hosts(
            NUM_OF_VMS,
            add_sgx=True,
            add_archive=True,
            add_geth=True
        )
    else:
        hosts = generate_hosts(
            NUM_OF_VMS,
            add_sgx=True,
            add_archive=False,
            add_geth=False
        )
    save(hosts, filepath=HOSTS_FILEPATH)


if __name__ == "__main__":
    main()
