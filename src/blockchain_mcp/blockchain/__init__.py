import os 
from .base_blockchain import BaseBlockchain
from .ether import Ether
from .vechain import Vechain
from . import bitcoin
from . import solana

ETHEREUM_NODE_URL = os.getenv("ETHEREUM_NODE_URL")
VECHAIN_NODE_URL = os.getenv("VECHAIN_NODE_URL")

def GetBlockChain(name:str) -> BaseBlockchain:
    if name == 'ethereum':
        return Ether(url=ETHEREUM_NODE_URL)
    elif name == 'vechain':
        pass

__all__ = [Ether, BaseBlockchain, Vechain]
