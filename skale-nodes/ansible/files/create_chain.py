#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2025-Present SKALE Labs
#
#   SKALE.py is free software: you can redistribute it and/or modify
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
#   along with SKALE.py.  If not, see <https://www.gnu.org/licenses/>.

import os
import logging
from eth_typing import HexStr

from skale import SkaleManager
from skale.utils.web3_utils import init_web3
from skale.wallets import Web3Wallet
from skale.utils.contracts_provision.main import (
    add_test_permissions,
    add_test2_schain_type,
    add_test4_schain_type,
    create_schain
)

logger = logging.getLogger(__name__)

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


def bootstrap_mirage(endpoint: str, alias_or_address: str, eth_private_key: HexStr) -> None:
    skale = init_skale_manager(endpoint, alias_or_address, eth_private_key)
    add_test_permissions(skale)
    add_test2_schain_type(skale)
    add_test4_schain_type(skale)

    create_schain(
        skale,
        schain_name=CHAIN_NAME,
        schain_type=1,
    )


if __name__ == '__main__':
    bootstrap_mirage(ENDPOINT, MANAGER_CONTRACTS, HexStr(ETH_PRIVATE_KEY))
