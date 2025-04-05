import os
from blockchain_mcp.base import BaseBlockchain
from blockchain_mcp.ethereum import Ethereum
from blockchain_mcp.vechain import Vechain
ETHEREUM_NODE_URL = os.getenv("ETHEREUM_NODE_URL")
VECHAIN_NODE_URL = os.getenv("VECHAIN_NODE_URL")
def GetBlockChain(name:str) -> BaseBlockchain:
    formatted_name = name.strip().lower()
    if formatted_name == 'ethereum':
        return Ethereum(url=ETHEREUM_NODE_URL)
    if formatted_name == 'vechain':
        return Vechain(VECHAIN_NODE_URL)
    else:
        raise ValueError(f"Unsupported blockchain: {name}")   