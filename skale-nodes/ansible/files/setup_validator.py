#   -*- coding: utf-8 -*-
#
#   This file is part of node-provisoning
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

import logging
import os
import random
import string

from skale import Skale
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3
from skale.utils.helper import init_default_logger
from skale.utils.account_tools import generate_account, send_eth
from skale.utils.contracts_provision.main import add_test_permissions

logger = logging.getLogger(__name__)
init_default_logger()

BASE_DIR = os.getenv('BASE_DIR')
ENDPOINT = os.getenv('ENDPOINT')
ABI_FILEPATH = os.path.join(BASE_DIR, 'manager.json')
ETH_PRIVATE_KEY = os.getenv('ETH_PRIVATE_KEY')
ETH_AMOUNT = float(os.getenv('ETH_AMOUNT'))
MIN_DELEGATION_AMOUNT = int(os.getenv('MIN_DELEGATION_AMOUNT'))
COMMISSION_RATE = int(os.getenv('COMMISSION_RATE'))
BASE_KEY_FILEPATH = os.path.join(BASE_DIR, 'validator-key.txt')
VALIDATOR_ID_FILEPATH = os.path.join(BASE_DIR, 'validator-id.txt')

NODES_NUMBER = int(os.getenv('NODES_NUMBER'))

web3 = init_web3(ENDPOINT)
wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
skale = Skale(ENDPOINT, ABI_FILEPATH, wallet)


def create_base_account_for_validator(validator_web3) -> dict:
    account_data = generate_account(validator_web3)
    send_eth(web3, wallet, account_data['address'], ETH_AMOUNT)
    return account_data


def create_skale_for_validator(account_dict, validator_web3) -> Skale:
    validator_skale = Skale(
        ENDPOINT, ABI_FILEPATH,
        Web3Wallet(account_dict['private_key'], validator_web3)
    )
    return validator_skale


def create_validator(name):
    validator_web3 = init_web3(ENDPOINT)
    validator_base_account = create_base_account_for_validator(validator_web3)
    validator_skale = create_skale_for_validator(validator_base_account,
                                                 validator_web3)

    tx_res = validator_skale.validator_service.register_validator(
        name=name,
        description=f'Validator for node {name}',
        fee_rate=COMMISSION_RATE,
        min_delegation_amount=MIN_DELEGATION_AMOUNT,
        wait_for=True
    )
    tx_res.raise_for_status()

    # New validator will have id equals to number of validators
    validator_id = skale.validator_service.number_of_validators()
    return validator_id, validator_base_account['private_key']


def whitelist_validator(validator_id):
    if not skale.validator_service._is_authorized_validator(validator_id):
        tx_res = skale.validator_service._enable_validator(validator_id,
                                                           wait_for=True)
        tx_res.raise_for_status()


def generate_random_name(length=5):
    return ''.join(random.choice(string.ascii_uppercase + string.digits))


def setup_validator():
    name = generate_random_name()
    vid, pkey = create_validator(name)

    whitelist_validator(vid)
    skale.constants_holder._set_msr(
        new_msr=0,
        wait_for=True
    )
    with open(BASE_KEY_FILEPATH, 'w') as pkey_file:
        pkey_file.write(pkey)
    with open(VALIDATOR_ID_FILEPATH, 'w') as vid_file:
        vid_file.write(str(vid))


def main():
    add_test_permissions(skale)
    setup_validator()


if __name__ == "__main__":
    main()
