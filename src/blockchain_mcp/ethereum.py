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
            self._validate_block_identifier(block_identifier)
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
                transactions:{block_info["transactions"].count()}
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
            tx_info = self.w3.eth.get_transaction(transaction_hash=tx_hash).__dict__
            print(f"Transaction: {tx_info}")
            data = f"""
                from: {tx_info["from"]},
                to: {tx_info["to"]},
                value: {tx_info["value"]},
                gas: {tx_info["gas"]},
                gasPrice: {tx_info["gasPrice"]},
                nonce: {tx_info["nonce"]},
                blockHash: {tx_info["blockHash"].hex()},
                blockNumber: {tx_info["blockNumber"]},
                transactionIndex: {tx_info["transactionIndex"]},
                input: {tx_info["input"]},
                v: {tx_info["v"]},
                r: {tx_info["r"].hex()},
                s: {tx_info["s"].hex()},
                chainId: {tx_info["chainId"]}
                """
            return BlockchainResponse(success=True, data=data, error=None)
        except ValueError as e:
            print(f"Value Error Get transaction {str(e)}")
            return BlockchainResponse(success=False, data=None, error=str(e))
        except TransactionNotFound as e:
            print(f"TransactionNotFound Get transaction {str(e)}")
            return BlockchainResponse(success=False, data="Block not found", error=str(e))
        except Web3Exception as e:
            print(f"Web3Exception Get transaction {str(e)}")
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
        
    def _validate_tx_hash(self, tx_hash: str):
        """Validate transaction hash format"""
        if not isinstance(tx_hash, str):
            print("Tx hash must be a string")
            raise ValueError("Tx hash must be string")
        if not re.match(r'^(0x)?[0-9a-fA-F]{64}$', tx_hash):
            print("Invalid Ethereum tx_hash format")
            raise ValueError("Invalid Ethereum tx_hash format")
    
    def _validate_address(self, address:str):
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
    #print(eth.get_block_info("latest"))
    #print(eth.get_balance("0xd3CdA913deB6f67967B99D67aCDFa1712C293601"))
    print(eth.get_transaction("0x1c31133a632433cd4896c6303a562926eb84378356dee33484ebf6b72391daed"))