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
from enum import Enum
from skale import SkaleManager
from skale.utils.web3_utils import init_web3
from skale.wallets import Web3Wallet
from skale.utils.contracts_provision.main import add_test_permissions, create_schain

CHAIN_NAME = os.environ['CHAIN_NAME']
ENDPOINT = os.environ['ENDPOINT']
ETH_PRIVATE_KEY = os.environ['ETH_PRIVATE_KEY']
MANAGER_CONTRACTS = os.environ['MANAGER_CONTRACTS']
CHAIN_TYPE = os.environ.get('CHAIN_TYPE', 'SMALL2').upper()


class SchainType(Enum):
    SMALL2 = [1, 2]
    SMALL4 = [1, 4]
    SMALL = [1, 16]
    MEDIUM2 = [16, 2]
    MEDIUM4 = [16, 4]
    MEDIUM = [16, 16]
    LARGE2 = [128, 2]
    LARGE4 = [128, 4]
    LARGE = [128, 16]
    TEST0_4 = [0, 4]
    TEST4_2 = [32, 2]
    TEST4_4 = [32, 4]
    TEST4 = [32, 16]
    EMPTY = [0, 0]


def get_chain_type_params(chain_type: str) -> list:
    try:
        return SchainType[chain_type].value
    except KeyError:
        print(f"Error: '{chain_type}' is not a valid SchainType. "
              f"Available types are: {[member.name for member in SchainType]}")
        raise


def add_schain_type(part_of_node, number_of_nodes):
    return skale.schains_internal.add_schain_type(
        part_of_node, number_of_nodes
    )


def get_schain_type_id(skale, type_parameters):
    n = skale.schains_internal.contract.functions.numberOfSchainTypes().call()
    for idx in range(1, n + 1):
        params = skale.schains_internal.get_schain_type(idx)
        print(f'PARAMS: {params}')
        if type_parameters == params:
            return idx
    return None


def prepare_and_create_chain(skale, chain_type=CHAIN_TYPE) -> None:
    add_test_permissions(skale)
    type_params = get_chain_type_params(chain_type)
    type_id = get_schain_type_id(skale, type_params)
    if type_id is None:
        print(f'sChain type {chain_type} '
              f'with {type_params[0]}, {type_params[1]} not found. Adding to contracts...')
        add_schain_type(type_params[0], type_params[1])
        type_id = get_schain_type_id(skale, type_params)

    create_schain(
        skale,
        schain_name=CHAIN_NAME,
        schain_type=type_id,
    )


def init_skale_manager(
    endpoint: str, alias_or_address: str, eth_private_key: HexStr
) -> SkaleManager:
    web3 = init_web3(endpoint)
    wallet = Web3Wallet(eth_private_key, web3)
    return SkaleManager(endpoint, alias_or_address, wallet)


if __name__ == '__main__':
    skale = init_skale_manager(ENDPOINT, MANAGER_CONTRACTS, HexStr(ETH_PRIVATE_KEY))
    prepare_and_create_chain(skale)
