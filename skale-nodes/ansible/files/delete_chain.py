#   -*- coding: utf-8 -*-
#
#   This file is part of node-provisoning
#
#   Copyright (C) 2025-Present SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   SKALE.py is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
from eth_typing import HexStr
from skale import SkaleManager
from skale.utils.web3_utils import init_web3
from skale.wallets import Web3Wallet

CHAIN_NAME = os.environ['CHAIN_NAME']
ENDPOINT = os.environ['ENDPOINT']
ETH_PRIVATE_KEY = os.environ['ETH_PRIVATE_KEY']
MANAGER_CONTRACTS = os.environ['MANAGER_CONTRACTS']


def init_skale_manager(
    endpoint: str, alias_or_address: str, eth_private_key: HexStr
) -> SkaleManager:
    web3 = init_web3(endpoint)
    wallet = Web3Wallet(eth_private_key, web3)
    return SkaleManager(endpoint, alias_or_address, wallet)


if __name__ == '__main__':
    skale = init_skale_manager(ENDPOINT, MANAGER_CONTRACTS, HexStr(ETH_PRIVATE_KEY))
    skale.manager.delete_schain_by_root(CHAIN_NAME, wait_for=True)
    print(f'Schain {CHAIN_NAME} is deleted!')
