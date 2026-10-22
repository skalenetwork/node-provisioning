#   -*- coding: utf-8 -*-
#
#   This file is part of node-provisioning
#
#   Copyright (C) 2026-Present SKALE Labs
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

"""Whitelist passive SKALE node IPs in SyncManager, so sChain nodes let them sync.

NODE_IPS is a JSON object {"<node name>": "<ip>", ...}. Each IP that no IP range covers
yet gets a one-address range named "<node name>-<ip>".
"""

import ipaddress
import json
import logging
import os

from eth_typing import HexStr
from skale import SkaleManager
from skale.contracts.manager.sync_manager import IpRange
from skale.utils.helper import init_default_logger
from skale.utils.web3_utils import init_web3
from skale.wallets import Web3Wallet

logger = logging.getLogger(__name__)
init_default_logger()

ENDPOINT = os.environ['ENDPOINT']
MANAGER_CONTRACTS = os.environ['MANAGER_CONTRACTS']
ETH_PRIVATE_KEY = os.environ['ETH_PRIVATE_KEY']
# The key anvil provided, empty without anvil
ANVIL_PRIVATE_KEY = os.getenv('ANVIL_PRIVATE_KEY')
NODE_IPS = json.loads(os.environ['NODE_IPS'])


def init_skale_manager(private_key: str) -> SkaleManager:
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(HexStr(private_key), web3)
    return SkaleManager(ENDPOINT, MANAGER_CONTRACTS, wallet)


def is_whitelisted(ip: str, ranges: list[IpRange]) -> bool:
    address = ipaddress.IPv4Address(ip)
    return any(
        ipaddress.IPv4Address(r.start_ip) <= address <= ipaddress.IPv4Address(r.end_ip)
        for r in ranges
    )


def ensure_sync_manager_role(skale: SkaleManager) -> None:
    sync_manager = skale.sync_manager
    role = sync_manager.sync_manager_role()
    address = skale.wallet.address
    if sync_manager.contract.functions.hasRole(role, address).call():
        return
    # Without anvil, this works only when the key is a SyncManager admin itself
    granter = init_skale_manager(ANVIL_PRIVATE_KEY) if ANVIL_PRIVATE_KEY else skale
    logger.info('Granting SYNC_MANAGER_ROLE to %s with %s', address, granter.wallet.address)
    granter.sync_manager.grant_sync_manager_role(address)


def whitelist(skale: SkaleManager, node_ips: dict[str, str]) -> None:
    sync_manager = skale.sync_manager
    ranges = [
        sync_manager.get_ip_range_by_index(index)
        for index in range(sync_manager.get_ip_ranges_number())
    ]
    missing = {}
    for name, ip in node_ips.items():
        if is_whitelisted(ip, ranges):
            logger.info('%s (%s) is already whitelisted', name, ip)
        else:
            missing[name] = ip
    if not missing:
        return
    ensure_sync_manager_role(skale)
    for name, ip in missing.items():
        logger.info('Whitelisting %s (%s)', name, ip)
        sync_manager.add_ip_range(f'{name}-{ip}', ip, ip)


if __name__ == '__main__':
    whitelist(init_skale_manager(ETH_PRIVATE_KEY), NODE_IPS)
