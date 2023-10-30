import os

from skale import Skale
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3, to_checksum_address


BASE_DIR = os.getenv('BASE_DIR')
ENDPOINT = os.getenv('ENDPOINT')
ADDRESS = os.getenv('ADDRESS').strip()
SIGNATURE = os.getenv('SIGNATURE').strip()
ABI_FILEPATH = os.path.join(BASE_DIR, 'manager.json')
ETH_PRIVATE_KEY = os.getenv('ETH_PRIVATE_KEY')


def main():
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    skale = Skale(ENDPOINT, ABI_FILEPATH, wallet)
    print(ETH_PRIVATE_KEY)
    print(ADDRESS)
    print(SIGNATURE)
    checksum_address = to_checksum_address(ADDRESS)
    validator_address = skale.wallet.address
    linked = skale.validator_service.get_linked_addresses_by_validator_address(
        validator_address
    )
    if checksum_address not in linked:
        skale.validator_service.link_node_address(
            node_address=checksum_address,
            signature=SIGNATURE,
            gas_price=skale.web3.eth.gas_price * 2
        )


if __name__ == '__main__':
    main()
