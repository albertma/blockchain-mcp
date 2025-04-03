from typing import Union
from .base_blockchain import BaseBlockchain, BlockchainResponse

class Vechain(BaseBlockchain):
    """
    Vechain区块链类
    """
    def __init__(self, rpc_url: str):
        super().__init__(rpc_url, 42)
        self.chain_name = "vechain"
        self.TX_HASH_PATTERN = r'^(0x)?[0-9a-fA-F]{64}$'
        
    def get_block_info(self, block_identifier: Union[int, str])->BlockchainResponse:
        pass