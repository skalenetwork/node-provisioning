import os
import subprocess
import sys
from functools import partial

from skale import Skale
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3, to_checksum_address


BASE_DIR = os.getenv('BASE_DIR')
ENDPOINT = os.getenv('ENDPOINT')
ABI_FILEPATH = os.path.join(BASE_DIR, 'manager.json')
print(ABI_FILEPATH)
ETH_PRIVATE_KEY = os.getenv('ETH_PRIVATE_KEY')

subprocess.run = partial(subprocess.run, stderr=subprocess.PIPE,
                         stdout=subprocess.PIPE)


def main():
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    skale = Skale(ENDPOINT, ABI_FILEPATH, wallet)
    address = sys.argv[1]
    validator_id = skale.validator_service.validator_id_by_address(
        skale.wallet.address)
    print(ETH_PRIVATE_KEY)
    print(skale.wallet.address)
    res = subprocess.run(['skale', 'node', 'signature', str(validator_id)])
    stdout = res.stdout.decode('utf-8')
    signature = str(stdout.strip().split()[1])
    checksum_address = to_checksum_address(address)
    tx_res = skale.validator_service.link_node_address(
        checksum_address, signature=signature, wait_for=True
    )
    tx_res.raise_for_status()


if __name__ == '__main__':
    main()
