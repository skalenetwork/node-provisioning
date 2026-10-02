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
from skale.utils.web3_utils import init_web3
from skale.wallets import Web3Wallet
from skale import FairManager


ENDPOINT = os.getenv('ENDPOINT')
FAIR_CONTRACTS = os.getenv('FAIR_CONTRACTS')
ETH_PRIVATE_KEY = os.getenv('ETH_PRIVATE_KEY')
RNG_ADDRESS = '0x0000000000000000000000000000000000000018'


def init_fair() -> FairManager:
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(HexStr(ETH_PRIVATE_KEY), web3)
    return FairManager(ENDPOINT, FAIR_CONTRACTS, wallet)


if __name__ == '__main__':
    fair = init_fair()
    skale_rng = fair.committee.skale_rng()
    fair.committee.set_rng(RNG_ADDRESS, skip_dry_run=True)
