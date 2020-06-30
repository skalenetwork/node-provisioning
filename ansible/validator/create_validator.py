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
import time

from skale import Skale
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3
from skale.utils.helper import init_default_logger

logger = logging.getLogger(__name__)
init_default_logger()

BASE_DIR = os.environ['BASE_DIR']
ENDPOINT = os.environ['ENDPOINT']
ABI_FILEPATH = os.path.join(BASE_DIR, 'manager.json')
OWNER_PRIVATE_KEY = os.environ['OWNER_PRIVATE_KEY']
VALIDATOR_PRIVATE_KEY = os.environ['VALIDATOR_PRIVATE_KEY']
VALIDATOR_ID_FILEPATH = os.path.join(BASE_DIR, 'validator-id')

web3 = init_web3(ENDPOINT)
wallet = Web3Wallet(OWNER_PRIVATE_KEY, web3)
skale = Skale(ENDPOINT, ABI_FILEPATH, wallet)


def create_skale_for_validator(validator_web3) -> Skale:
    validator_skale = Skale(
        ENDPOINT, ABI_FILEPATH,
        Web3Wallet(VALIDATOR_PRIVATE_KEY, validator_web3)
    )
    return validator_skale


def create_validator():
    validator_web3 = init_web3(ENDPOINT)
    validator_skale = create_skale_for_validator(validator_web3)

    name = 'SKALE FOUNDATION'
    description = 'SKALE FOUNDATION VALIDATOR'
    commission_rate = 0
    min_delegation_amount = 0
    tx_res = validator_skale.validator_service.register_validator(
        name=name,
        description=description,
        fee_rate=commission_rate,
        min_delegation_amount=min_delegation_amount,
        wait_for=True
    )
    tx_res.raise_for_status()

    # New validator will have id equals to number of validators
    validator_id = skale.validator_service.number_of_validators()
    return validator_id


def whitelist_validator(validator_id):
    if not skale.validator_service._is_authorized_validator(validator_id):
        tx_res = skale.validator_service._enable_validator(validator_id,
                                                           wait_for=True)
        tx_res.raise_for_status()


def setup_validator():
    id = create_validator()
    time.sleep(5)
    whitelist_validator(id)
    time.sleep(5)
    with open(VALIDATOR_ID_FILEPATH, 'w') as key_file:
        key_file.write(str(id))


def main():
    print(ENDPOINT)
    print(BASE_DIR)
    print(OWNER_PRIVATE_KEY[:4])
    print(VALIDATOR_PRIVATE_KEY[:4])
    time.sleep(5)
    setup_validator()


if __name__ == "__main__":
    main()
