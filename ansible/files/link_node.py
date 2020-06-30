import os

from skale import Skale
from skale.wallets import Web3Wallet
from skale.utils.account_tools import send_ether
from skale.utils.web3_utils import init_web3, to_checksum_address


BASE_DIR = os.getenv('BASE_DIR')
ENDPOINT = os.getenv('ENDPOINT')
ABI_FILEPATH = os.path.join(BASE_DIR, 'manager.json')
ETH_PRIVATE_KEY = os.getenv('ETH_PRIVATE_KEY')
ADDRESS = os.getenv('ADDRESS').strip()
SIGNATURE = os.getenv('SIGNATURE').strip()
NODE_ETH_AMOUNT = float(os.getenv('NODE_ETH_AMOUNT'))


def main():
    validator_pk_path = os.path.join(BASE_DIR, 'validator-pk')
    with open(validator_pk_path) as pk_file:
        pk = pk_file.read().strip()

    print(ADDRESS)
    print(SIGNATURE)
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(pk, web3)
    skale = Skale(ENDPOINT, ABI_FILEPATH, wallet)

    checksum_address = to_checksum_address(ADDRESS)
    skale.validator_service.link_node_address(
        checksum_address,
        signature=SIGNATURE,
        wait_for=True
    )
    print('Node is linked')
    send_ether(web3, wallet, ADDRESS, NODE_ETH_AMOUNT, wait_for=True)


if __name__ == '__main__':
    main()
