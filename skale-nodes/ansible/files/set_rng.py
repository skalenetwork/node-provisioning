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
    fair.committee.set_rng(RNG_ADDRESS)
