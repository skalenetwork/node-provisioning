#   -*- coding: utf-8 -*-
#
#   This file is part of node-automation
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
import json

from skale import Skale
from skale.utils.helper import private_key_to_address, init_default_logger
from skale.utils.account_tools import init_wallet, generate_accounts

logger = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
ABI_FILEPATH = os.path.join(CURRENT_DIR, 'data.json')

n_wallets = os.environ['N_WALLETS']
skale_amount = os.environ['SKALE_AMOUNT']
eth_amount = os.environ['ETH_AMOUNT']

init_default_logger()

ENDPOINT = os.environ['ENDPOINT']

skale = Skale(ENDPOINT, ABI_FILEPATH)
base_wallet = init_wallet()

accounts = generate_accounts(skale, base_wallet, n_wallets, skale_amount, eth_amount, True)

for i, account  in enumerate(accounts):
    filename = f'wallet-{i}.txt'
    filepath = os.path.join(CURRENT_DIR, 'wallets', filename)
    #content = f'#!/usr/bin/env bash\nexport ETH_PRIVATE_KEY={account["private_key"]}'
    content = account["private_key"]
    with open(filepath, 'w') as outfile:
         logger.info(f'Saving info to {filename}')
         outfile.write(content)


#save_info('node_wallets.json', result)
