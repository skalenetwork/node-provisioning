import ipaddress
import random


def generate_random_ip() -> ipaddress.IPv4Address:
    random_int = random.randint(0, 2**32 - 1)
    ip_object = ipaddress.IPv4Address(random_int)
    return ip_object


if __name__ == '__main__':
    random_ip_object = generate_random_ip()
    print(random_ip_object)
