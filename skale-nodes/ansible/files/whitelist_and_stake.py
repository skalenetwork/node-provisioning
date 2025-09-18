import logging
import os

from skale import FairManager
from eth_typing import HexStr
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3
from skale.utils.helper import init_default_logger

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

if __name__ == '__main__':

    fair = init_fair_manager()
    nodes = fair.nodes.get_active_node_ids()
    logger.debug(nodes)
    for node_id in nodes:
        try:
            if fair.status.is_whitelisted(node_id):
                logger.info(f'Node {node_id} is already whitelisted. Skipping...')
            else:
                fair.status.whitelist_node(node_id)
                logger.info(f'Node {node_id} is successfully whitelisted')
        except Exception as e:
            logger.warning(f'Cannot whitelist node {node_id}: {e}')
        try:
            fair.staking.stake(node_id, value=WEI_AMOUNT)
            logger.info(f'Node {node_id} is successfully staked')
        except Exception as e:
            logger.warning(f'Cannot stake node {node_id}: {e}')

