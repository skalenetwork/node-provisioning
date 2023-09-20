#   -*- coding: utf-8 -*-
#
#   This file is part of node-provisoning
#
#   Copyright (C) 2023 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import json
import logging
import os

from skale import Skale
from skale.wallets import Web3Wallet
from skale.utils.helper import ip_from_bytes
from skale.utils.web3_utils import init_web3

logger = logging.getLogger(__name__)

BASE_DIR = os.getenv('BASE_DIR')
ENDPOINT = os.getenv('ENDPOINT')
ABI_FILEPATH = os.path.join(BASE_DIR, 'manager.json')
ETH_PRIVATE_KEY = os.getenv('ETH_PRIVATE_KEY')


def dropped_irrelevant(node_data):
    return {
        'name': node_data['name'],
        'ip': ip_from_bytes(node_data['ip'])
    }


def get_nodes_by_schain(skale, schain):
    node_ids = skale.schains_internal.get_node_ids_for_schain(schain)
    return sorted([
        dropped_irrelevant(skale.nodes.get(nid))
        for nid in node_ids
    ], key=lambda node: node['name'])


def get_all_schains(skale):
    return [
        skale.schains.get(sid)['name']
        for sid in skale.schains_internal.get_all_schains_ids()
        if sid
    ]


def get_schains_by_nodes(skale, schains):
    schains_by_nodes = {}
    for schain in schains:
        nodes = get_nodes_by_schain(skale, schain)
        for node in nodes:
            ip = node['ip']
            if ip in schains_by_nodes:
                schains_by_nodes[ip].append(schain)
            else:
                schains_by_nodes[ip] = [schain]
    return schains_by_nodes


def get_nodes_by_schains(skale, schains):
    return {
        schain: get_nodes_by_schain(skale, schain)
        for schain in schains
    }


def main():
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    skale = Skale(ENDPOINT, ABI_FILEPATH, wallet)

    parser = argparse.ArgumentParser(
        prog='FetchSchainsNodes',
        description='Fetch node/schain info from mainnet'
    )
    parser.add_argument('-n', '--nodes', action='store_true')
    parser.add_argument('-s', '--schains', action='store_true')

    args = parser.parse_args()

    schains = get_all_schains(skale)

    if args.schains:
        schains_by_nodes = get_schains_by_nodes(skale, schains)
        print(json.dumps(schains_by_nodes))
    else:
        nodes_by_schains = get_nodes_by_schains(skale, schains)
        print(json.dumps(nodes_by_schains))


if __name__ == '__main__':
    main()
