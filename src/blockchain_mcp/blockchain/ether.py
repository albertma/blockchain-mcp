from argparse import ArgumentError
from web3 import Web3, AsyncWeb3
import os
from web3.exceptions import Web3Exception
from .base_blockchain import BaseBlockchain, BlockchainResponse
from typing import Dict, Optional, Union
import re

class Ethereum(BaseBlockchain):
    def __init__(self, url):
        super().__init__(rpc_url=url, chain_id=1)
        self.network_id = 1
        self.w3 = Web3(Web3.HTTPProvider(url))
        self.chain_name = "ethereum"

    def get_block_info(self, block_identifier: Union[int, str])->BlockchainResponse:
        """Get latest Ethereum block information

        Returns:
            dict: A dictionary of block information
        """
        try:
            block_info = self.w3.eth.get_block(block_identifier).__dict__
            data =  f"""
                baseFeePerGas: {block_info["baseFeePerGas"]},
                excessBlobGas: {block_info["excessBlobGas"]},
                gasLimit: {block_info["gasLimit"]},
                gasUsed: {block_info["gasUsed"]},
                hash: {block_info["hash"].hex()},
                miner: {block_info["miner"]},
                nonce: {block_info["nonce"].hex()},
                number: {block_info["number"]},
                mixHash: {block_info["mixHash"].hex()},
                size: {block_info["size"]},
                timestamp: {block_info["timestamp"]},
                parentBeaconBlockRoot:{block_info["parentBeaconBlockRoot"].hex()},
                parentHash:{block_info["parentHash"].hex()},
                stateRoot:{block_info["stateRoot"].hex()},
                receiptsRoot:{block_info["receiptsRoot"].hex()},
                transactions:{[item.hex() for item in block_info["transactions"]]}
            """
            return BlockchainResponse(success=True, data=data, error=None)
            
        except Web3Exception as e:
            print(f"Get block info {str(e)}")
            return BlockchainResponse(success=False, data=None, error=e)
        
    def get_balance(self, address: str) -> BlockchainResponse:
        """Get balance of address

        Args:
            addr (_type_): the holder address of ether. eg. "0xd3CdA913deB6f67967B99D67aCDFa1712C293601"

        Returns:
            float: balance of ether
        """
        wei_balance = self.w3.eth.get_balance(address)
        try:
            balance = round((wei_balance // 10**13) / 100000, 5)
            data = f"""
                Balance:{balance}Ether
            """
            return BlockchainResponse(success=True, data=data)
        except (ValueError, TypeError) as e:
            print(f"Error: {str(e)}")
            return BlockchainResponse
        
    def get_transaction(self, tx_hash: str) -> BlockchainResponse:
        if not self._validate_tx_hash(tx_hash=tx_hash):
            return BlockchainResponse(success=False, error= ArgumentError("Invalid tx_hash format"))
        try:
            tx_dict = self.w3.eth.get_transaction(transaction_hash=tx_hash).__dict__
            data = f"""
                blockHash: {tx_dict["blockHash"].hex()},
                blockNumber: {tx_dict["blockNumber"]},
                from: {tx_dict["from"]},
                gas: {tx_dict["gas"]},
                gasPrice: {tx_dict["gasPrice"]},
                hash: {tx_dict["hash"].hex()},
                input: {tx_dict["input"]},
                nonce: {tx_dict["nonce"]},
                to: {tx_dict["to"]},
                transactionIndex: {tx_dict["transactionIndex"]},
                value: {tx_dict["value"]},
                v: {tx_dict["v"]},
                r: {tx_dict["r"].hex()},
                s: {tx_dict["s"].hex()}
                """
            return BlockchainResponse(success=True, data=data)
        except Web3Exception as e:
            print(f"Get transaction {str(e)}")
            return BlockchainResponse(success=False, data=None, error=e)
    
if __name__ == "__main__":
    ETHEREUM_NODE_URL = os.getenv("ETHEREUM_NODE_URL")
    eth = Ethereum(ETHEREUM_NODE_URL)
    print(eth.get_block_info("latest"))