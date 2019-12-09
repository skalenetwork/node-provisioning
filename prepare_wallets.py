#   -*- coding: utf-8 -*-
#
#   This file is part of skale-node
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import logging

from skale import Skale
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3
from skale.utils.helper import init_default_logger
from skale.utils.account_tools import generate_accounts

logger = logging.getLogger(__name__)
init_default_logger()

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
ENDPOINT = os.environ['ENDPOINT']
ABI_FILEPATH = os.path.join(CURRENT_DIR, 'manager.json')
ETH_PRIVATE_KEY = os.environ['ETH_PRIVATE_KEY']

N_WALLETS = os.environ['N_WALLETS']
SKALE_AMOUNT = os.environ['SKALE_AMOUNT']
ETH_AMOUNT = os.environ['ETH_AMOUNT']

web3 = init_web3(ENDPOINT)
wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
skale = Skale(ENDPOINT, ABI_FILEPATH, wallet)


def save_wallet_info(i, account):
    filename = f'wallet-{i}.txt'
    filepath = os.path.join(CURRENT_DIR, 'wallets', filename)
    with open(filepath, 'w') as outfile:
        logger.info(f'Saving info to {filename}')
        outfile.write(account["private_key"])


def prepare_wallets():
    accounts = generate_accounts(skale, skale.wallet, N_WALLETS, SKALE_AMOUNT, ETH_AMOUNT, True)
    for i, account in enumerate(accounts):
        save_wallet_info(i, account)


if __name__ == "__main__":
    prepare_wallets()
