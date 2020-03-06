import logging
import os

from skale import Skale
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3, wait_receipt
from skale.utils.helper import init_default_logger

logger = logging.getLogger(__name__)
init_default_logger()

BASE_DIR = os.getenv('BASE_DIR')
ENDPOINT = os.getenv('ENDPOINT')
ABI_FILEPATH = os.path.join(BASE_DIR, 'manager.json')
ETH_PRIVATE_KEY = os.getenv('ETH_PRIVATE_KEY')

web3 = init_web3(ENDPOINT)
wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
skale = Skale(ENDPOINT, ABI_FILEPATH, wallet)


def remove_active_nodes():
    for node_id in skale.nodes_data.get_active_node_ids():
        skale.manager.delete_node_by_root(node_id, wait_for=True)


def get_all_schains_names(skale):
    schains_ids = skale.schains_data.get_all_schains_ids()
    names = [skale.schains_data.get(sid).get('name')
             for sid in schains_ids]
    return names


def remove_all_schains():
    schain_names = get_all_schains_names(skale)
    for name in schain_names:
        skale.manager.delete_schain(name, wait_for=True)


def cleanup():
    remove_all_schains()
    remove_active_nodes()


if __name__ == "__main__":
    cleanup()
