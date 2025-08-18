#   This file is part of node-provisioning
#
#   Copyright (C) 2025-Present SKALE Labs
#
#   node-provisioning is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   node-provisioning is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with node-provisioning.  If not, see <https://www.gnu.org/licenses/>.

import codecs
import logging
import os

from eth_keys import keys
from eth_typing import HexStr
from skale import FairManager
from skale.utils.helper import init_default_logger
from skale.utils.web3_utils import init_web3
from skale.wallets import Web3Wallet

logger = logging.getLogger(__name__)
init_default_logger()

BASE_DIR = os.getenv('BASE_DIR')
ENDPOINT = os.getenv('ENDPOINT')
FAIR_CONTRACTS = os.getenv('FAIR_CONTRACTS')
ETH_PRIVATE_KEY = os.getenv('ETH_PRIVATE_KEY')
PASSIVE_FAIR_IP = os.getenv('PASSIVE_FAIR_IP')
PASSIVE_FAIR_PORT = 10000
PASSIVE_ID_FILEPATH = os.path.join(BASE_DIR, 'passive-id.txt')


def init_fair() -> FairManager:
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(HexStr(ETH_PRIVATE_KEY), web3)
    return FairManager(ENDPOINT, FAIR_CONTRACTS, wallet)


if __name__ == '__main__':
    fair = init_fair()
    fair.nodes.register_passive(PASSIVE_FAIR_IP, PASSIVE_FAIR_PORT)
    private_key_bytes = codecs.decode(ETH_PRIVATE_KEY, 'hex')
    priv_key = keys.PrivateKey(private_key_bytes)
    pub_key = priv_key.public_key
    address = pub_key.to_checksum_address()
    passive_ids = fair.nodes.get_passive_node_ids_for_address(address)
    logger.info(f'All passive nodes for current address: {passive_ids}')
    if len(passive_ids):
        new_passive_node_id = passive_ids[-1]
        logger.info(f'New passive node ID: {new_passive_node_id}')
        with open(PASSIVE_ID_FILEPATH, 'w') as passive_id_file:
            passive_id_file.write(str(new_passive_node_id))
