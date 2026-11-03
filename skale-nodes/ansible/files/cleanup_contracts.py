import logging
import os
import sys
from eth_typing import HexStr

from skale import SkaleManager
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3
from skale.utils.helper import init_default_logger
from skale.utils.contracts_provision.main import cleanup_nodes, cleanup_schains

logger = logging.getLogger(__name__)
init_default_logger()

ENDPOINT = os.getenv('ENDPOINT')
MANAGER_CONTRACTS = os.getenv('MANAGER_CONTRACTS')
ETH_PRIVATE_KEY = os.getenv('ETH_PRIVATE_KEY')


def init_skale_manager(
    endpoint: str, alias_or_address: str, eth_private_key: HexStr
) -> SkaleManager:
    web3 = init_web3(endpoint)
    wallet = Web3Wallet(eth_private_key, web3)
    return SkaleManager(endpoint, alias_or_address, wallet)


def remove_active_nodes(skale):
    logger.info('Removing all active nodes...')
    cleanup_nodes(skale)
    logger.info('Finished removing active nodes')


def remove_all_schains(skale):
    logger.info('Removing all chains...')
    cleanup_schains(skale)
    logger.info('Finished removing chains')


def cleanup(skale):
    remove_all_schains(skale)
    remove_active_nodes(skale)


if __name__ == '__main__':
    skale = init_skale_manager(ENDPOINT, MANAGER_CONTRACTS, HexStr(ETH_PRIVATE_KEY))
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == 'remove_chains':
            remove_all_schains(skale)
        elif action == 'remove_nodes':
            remove_active_nodes(skale)
        else:
            logger.error(f'Unknown action: {action}. Please use "remove_chains" or "remove_nodes"')
            sys.exit(1)
    else:
        logger.info('No action specified, running full cleanup')
        cleanup(skale)
