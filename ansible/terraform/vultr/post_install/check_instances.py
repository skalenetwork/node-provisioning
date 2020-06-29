from time import sleep

from vultr import Vultr
import json
import socket
import os

VULTR_API_KEY = os.getenv('VULTR_API_KEY')
vultr = Vultr(VULTR_API_KEY)
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'hosts_info.json')
SOCKET_TIMEOUT = 30


def check_ssh(server_ip, port=22):
    try:
        socket.setdefaulttimeout(SOCKET_TIMEOUT)
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.connect((server_ip, port))
    except Exception as ex:
        return False
    else:
        test_socket.close()
    return True


def get_hosts_mapping():
    with open(OUTPUT_PATH) as droplets_json:
        data = json.load(droplets_json)
        ids = data['ids_of_droplets']['value']
        ips = data['public_ips']['value']
    return [{'id': host[0], 'ip': host[1]}
            for host in zip(ids.values(), ips.values())]


def get_failed_hosts(hosts):
    failed = []
    for host in hosts:
        if not check_ssh(host['ip']):
            failed.append(host)
    return failed


def restart_failed_hosts(hosts):
    for host in hosts:
        print(f'Reinstall host: {host}')
        vultr.server.reinstall(host['id'])
        while vultr.server.list(host['id'])['power_status'] != 'running':
            print('Reinstalling host...')
            sleep(10)
    sleep(60)


def main():
    hosts = get_hosts_mapping()
    failed_hosts = get_failed_hosts(hosts)
    while len(failed_hosts) > 0:
        print(f'Failed hosts: {failed_hosts}')
        restart_failed_hosts(failed_hosts)
        failed_hosts = get_failed_hosts(hosts)


if __name__ == '__main__':
    main()
