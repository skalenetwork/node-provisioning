#   -*- coding: utf-8 -*-
#
#   This file is part of node-provisioning
#
#   Copyright (C) 2019 SKALE Labs
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

import os
import logging

from skale import Skale
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3
from skale.utils.helper import init_default_logger
from skale.utils.account_tools import send_eth
from skale.utils.web3_utils import to_checksum_address


BASE_DIR = os.getenv('BASE_DIR')
ENDPOINT = os.getenv('ENDPOINT')
ABI_FILEPATH = os.path.join(BASE_DIR, 'manager.json')
ETH_PRIVATE_KEY = os.getenv('ETH_PRIVATE_KEY')
ADDRESS = os.getenv('ADDRESS')
AMOUNT = float(os.getenv('AMOUNT'))

logger = logging.getLogger(__name__)
init_default_logger()


def init_web3_skale():
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    return Skale(ENDPOINT, ABI_FILEPATH, wallet)


def main():
    skale = init_web3_skale()
    address = to_checksum_address(ADDRESS)
    send_eth(skale.web3, skale.wallet, address, AMOUNT)


if __name__ == "__main__":
    main()
