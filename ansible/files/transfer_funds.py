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
import ast
import subprocess
from subprocess import PIPE

from skale import Skale
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3
from skale.utils.helper import init_default_logger
from skale.utils.account_tools import (send_ether, send_tokens,
                                       check_ether_balance,
                                       check_skale_balance)


BASE_DIR = os.getenv('BASE_DIR')
ENDPOINT = os.getenv('ENDPOINT')
ABI_FILEPATH = os.path.join(BASE_DIR, 'manager.json')
ETH_PRIVATE_KEY = os.environ['ETH_PRIVATE_KEY']

GAS_COMMISSION_FACTOR = 0.7


logger = logging.getLogger(__name__)
init_default_logger()


def run_cmd(cmd, env={}, shell=False):
    logger.info(f'Running: {cmd}')
    res = subprocess.run(cmd, shell=shell, stdout=PIPE,
                         stderr=PIPE, env={**env, **os.environ})
    if res.returncode:
        logger.error('Error during shell execution:')
        logger.error(res.stderr.decode('UTF-8').rstrip())
        raise subprocess.CalledProcessError(res.returncode, cmd)
    return res


def format_output(res):
    return (res.stdout.decode('UTF-8').rstrip(),
            res.stderr.decode('UTF-8').rstrip())


def init_web3_skale():
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    return Skale(ENDPOINT, ABI_FILEPATH, wallet)


def get_node_wallet_address():
    cmd = 'skale wallet info -f json'
    res = run_cmd(cmd, shell=True)
    out, _ = format_output(res)
    wallet_info = ast.literal_eval(out)
    return wallet_info['address']


def send_funds(skale, address, skale_amount, eth_amount):
    send_tokens(skale, skale.wallet, address, skale_amount)
    send_ether(skale.web3, skale.wallet, address, eth_amount)
    check_ether_balance(skale.web3, address)
    check_skale_balance(skale, address)


def get_transfer_amount(skale):
    address = skale.wallet.address
    ether_balance = check_ether_balance(skale.web3, address)
    skale_balance = check_skale_balance(skale, address)
    return float(ether_balance) * GAS_COMMISSION_FACTOR, skale_balance


def _run_tm_manager(skale):
    send_ether(skale.web3, skale.wallet, skale.wallet.address, 0)


def main():
    skale = init_web3_skale()
    _run_tm_manager(skale)  # todo: temporary measure, remove later
    address = get_node_wallet_address()
    # todo: temporary fix
    # eth_amount, skale_amount = get_transfer_amount(skale)
    eth_amount, skale_amount = 0.21, 0
    send_funds(skale, address, skale_amount, eth_amount)


if __name__ == "__main__":
    main()
