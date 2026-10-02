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
import sys

from eth_typing import HexStr
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3
from skale.utils.helper import init_default_logger
from skale.utils.account_tools import send_eth
from skale.utils.web3_utils import to_checksum_address


BASE_DIR = os.getenv('BASE_DIR')
ENDPOINT = os.getenv('ENDPOINT')
ETH_PRIVATE_KEY = os.getenv('ETH_PRIVATE_KEY')
ADDRESS = os.getenv('ADDRESS')
AMOUNT = float(os.getenv('AMOUNT'))
TARGET_PRIVATE_KEY = os.getenv('TARGET_PRIVATE_KEY')
ALLOWED_TS_DIFF = int(os.getenv('ALLOWED_TS_DIFF', 300))

logger = logging.getLogger(__name__)
init_default_logger()


def main():
    web3 = init_web3(ENDPOINT)

    # If using anvil, disable the stale check middleware to prevent StaleBlockchain errors
    if ALLOWED_TS_DIFF < 0:
        if 'stalecheck' in web3.middleware_onion:
            logger.info("Disabling stalecheck middleware for anvil.")
            web3.middleware_onion.remove('stalecheck')
        else:
            logger.info("Stalecheck middleware not found, no action needed.")

    wallet = Web3Wallet(HexStr(ETH_PRIVATE_KEY), web3)

    target_address = None
    if ADDRESS:
        target_address = ADDRESS
    elif TARGET_PRIVATE_KEY:
        logger.info("ADDRESS not provided, deriving from TARGET_PRIVATE_KEY.")
        target_wallet = Web3Wallet(HexStr(TARGET_PRIVATE_KEY), web3)
        target_address = target_wallet.address

    if not target_address:
        logger.critical("Error: Neither ADDRESS nor TARGET_PRIVATE_KEY environment variables were provided.")
        sys.exit(1)

    checksum_address = to_checksum_address(target_address)
    logger.info(f"Sending {AMOUNT} ETH to {checksum_address}...")
    send_eth(web3, wallet, checksum_address, AMOUNT)
    logger.info("Transfer successful.")


if __name__ == '__main__':
    main()
