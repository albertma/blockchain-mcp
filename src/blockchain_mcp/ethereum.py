from argparse import ArgumentError
from web3 import Web3
import os
from web3.exceptions import Web3Exception, TransactionNotFound, BlockNotFound
from typing import Union
from blockchain_mcp.base import BaseBlockchain, BlockchainResponse
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
            self.__validate_block_identifier(block_identifier)
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
        except BlockNotFound as e:
            print(f"Get block info {str(e)}")
            return BlockchainResponse(success=False, data="Block not found", error=str(e))    
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
       
        try:
            self._validate_address(address=address)
            wei_balance = self.w3.eth.get_balance(address)
            balance = round(wei_balance / (10**18), 5)
            data = f"""
                Balance:{balance} Ether
            """
            return BlockchainResponse(success=True, data=data, error=None)
        except (ValueError, TypeError) as e:
            print(f"Error: {str(e)}")
            return BlockchainResponse(success=False, data=None, error=str(e))
        except Web3Exception as e:
            print(f"Error: {str(e)}")
            return BlockchainResponse(success=False, data=None, error=str(e))
        
    def get_transaction(self, tx_hash: str) -> BlockchainResponse:
        try:
            self._validate_tx_hash(tx_hash=tx_hash)
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
        except ValueError as e:
            print(f"Get transaction {str(e)}")
            return BlockchainResponse(success=False, data=None, error=str(e))
        except TransactionNotFound as e:
            print(f"Get transaction {str(e)}")
            return BlockchainResponse(success=False, data="Block not found", error=str(e))
        except Web3Exception as e:
            print(f"Get transaction {str(e)}")
            return BlockchainResponse(success=False, data=None, error=e)
        
    def _validate_block_identifier(self, block_identifier: Union[int, str]):
        if isinstance(block_identifier, int):
            if block_identifier < 0:
                raise ValueError("Block number must be a positive integer")
        elif isinstance(block_identifier, str):
            if block_identifier == "latest":
                return
            elif not block_identifier.startswith("0x") or len(block_identifier) != 66:
                raise ValueError("Block hash must start with '0x' and be 66 characters long")
        else:
            raise ValueError("Block identifier must be an integer or a string")
        
    def _validate_tx_hash(self, tx_hash: str) -> bool:
        """Validate transaction hash format"""
        if not isinstance(tx_hash, str):
            raise ValueError("Tx hash must be string")
        if not re.match(r'^(0x)?[0-9a-fA-F]{64}$', tx_hash):
            raise ValueError("Invalid Ethereum tx_hash format")
    
    def _validate_address(self, address:str)->str:
        """Convert address to checksum format"""
        if not isinstance(address, str):
            raise ValueError("Address must be a string")
        if not re.match(r'^(0x)?[0-9a-fA-F]{40}$', address):
            raise ValueError("Invalid Ethereum address format")
        
    
if __name__ == "__main__":
    ETHEREUM_NODE_URL = os.getenv("ETHEREUM_NODE_URL")
    if not ETHEREUM_NODE_URL:
        raise ValueError("ETHEREUM_NODE_URL environment variable is not set")
    eth = Ethereum(ETHEREUM_NODE_URL)
    # print(eth.get_block_info("latest"))
    print(eth.get_balance("0xd3CdA913deB6f67967B99D67aCDFa1712C293601"))
    #print(eth.get_transaction("0x5f3b8c2e4d1a7c6f8e9b2f3a4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e"))