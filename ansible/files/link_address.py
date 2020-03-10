import os
import sys

from skale import Skale
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3, check_receipt


BASE_DIR = os.getenv('BASE_DIR')
ENDPOINT = os.getenv('ENDPOINT')
ABI_FILEPATH = os.path.join(BASE_DIR, 'manager.json')
ETH_PRIVATE_KEY = os.getenv('ETH_PRIVATE_KEY')


def main():
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    skale = Skale(ENDPOINT, ABI_FILEPATH, wallet)
    address = sys.argv[1]
    tx_res = skale.delegation_service.link_node_address(
        address, wait_for=True
    )
    check_receipt(tx_res.receipt)


if __name__ == '__main__':
    main()
