import logging
import os

from eth_typing import HexStr
from skale import FairManager
from skale.utils.helper import init_default_logger
from skale.utils.web3_utils import init_web3
from skale.wallets import Web3Wallet

ENDPOINT = os.getenv('ENDPOINT')
FAIR_CONTRACTS = os.getenv('FAIR_CONTRACTS')
ETH_PRIVATE_KEY = os.getenv('ETH_PRIVATE_KEY')
WEI_AMOUNT = int(os.getenv('WEI_AMOUNT'))

logger = logging.getLogger(__name__)
init_default_logger()


def init_fair_manager() -> FairManager:
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(HexStr(ETH_PRIVATE_KEY), web3)
    return FairManager(ENDPOINT, FAIR_CONTRACTS, wallet=wallet)


def process_node(fair_manager: FairManager, node_id: int) -> None:
    try:
        if fair_manager.status.is_whitelisted(node_id):
            logger.info(f'Node {node_id} is already whitelisted. Skipping whitelisting.')
        else:
            fair_manager.status.whitelist_node(node_id)
            logger.info(f'Node {node_id} was successfully whitelisted.')
    except Exception as e:
        logger.warning(f'Could not whitelist node {node_id}: {e}')

    try:
        fair_manager.staking.stake(node_id, value=WEI_AMOUNT)
        logger.info(f'Node {node_id} was successfully staked with {WEI_AMOUNT} Wei.')
    except Exception as e:
        logger.warning(f'Could not stake node {node_id}: {e}')


def main() -> None:
    fair_manager = init_fair_manager()

    try:
        nodes_to_process = fair_manager.nodes.get_active_node_ids()
        if not nodes_to_process:
            logger.info('No active nodes found')
            return
        logger.info(f'Found active nodes: {nodes_to_process}')
    except Exception as e:
        logger.critical(f'Failed to get active node IDs: {e}')
        return

    for node_id in nodes_to_process:
        process_node(fair_manager, node_id)


if __name__ == '__main__':
    main()
