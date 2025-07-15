#   -*- coding: utf-8 -*-
#
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

import os
from eth_typing import HexStr
from skale import SkaleManager
from skale.utils.web3_utils import init_web3
from skale.wallets import Web3Wallet
from skale.wallets.web3_wallet import generate_wallet
from skale.utils.contracts_provision.fair import (
    link_node_address, register_node, add_test_permissions, init_skale_from_wallet
)
from skale.utils.contracts_provision.main import (
    set_test_msr, create_validator, enable_validator, validator_exist
)
from skale.utils.account_tools import send_eth

ETH_AMOUNT = 0.2
ENDPOINT = os.environ['ENDPOINT']
ETH_PRIVATE_KEY = os.environ['ETH_PRIVATE_KEY']
MANAGER_CONTRACTS = os.environ['MANAGER_CONTRACTS']


def init_skale_manager(
    endpoint: str, alias_or_address: str, eth_private_key: HexStr
) -> SkaleManager:
    web3 = init_web3(endpoint)
    wallet = Web3Wallet(eth_private_key, web3)
    return SkaleManager(endpoint, alias_or_address, wallet)


def setup_validator(skale: SkaleManager):
    """Create and activate a validator"""
    set_test_msr(skale, msr=0)
    print('Address', skale.wallet.address)
    if not validator_exist(skale):
        create_validator(skale)
    else:
        print('Skipping default validator creation')
    validator_id = skale.validator_service.validator_id_by_address(skale.wallet.address)
    if not skale.validator_service.get(validator_id)['trusted']:
        enable_validator(skale, validator_id)


def fix_zero_node(skale):
    wallet = generate_wallet(skale.web3)
    print(f'Node Address: {wallet.address}')
    send_eth(skale.web3, skale.wallet, wallet.address, ETH_AMOUNT)
    add_test_permissions(skale)
    setup_validator(skale)
    link_node_address(skale, wallet)
    node_skale = init_skale_from_wallet(skale, wallet)
    register_node(node_skale)
    skale.nodes.init_exit(0)
    skale.manager.node_exit(0)


if __name__ == '__main__':
    skale = init_skale_manager(ENDPOINT, MANAGER_CONTRACTS, HexStr(ETH_PRIVATE_KEY))
    fix_zero_node(skale)
