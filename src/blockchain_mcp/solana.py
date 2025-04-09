
from typing import Union
from blockchain_mcp.base import BaseBlockchain, BlockchainResponse
import requests
import json

class SolanaBlockchain(BaseBlockchain):
    """
    Solana blockchain class for handling Solana-specific operations.
    """

    def __init__(self, url: str):
        """
        Initialize the Solana blockchain instance.

        Args:
            config (dict): Configuration dictionary containing Solana-specific settings.
        """
        super().__init__(rpc_url=url, chain_id=101)
        self.chain_name = "solana"
    
    def get_block_info(self, block_identifier: Union[int, str]) -> BlockchainResponse:
        """
        Get Solana block information.

        Args:
            block_identifier (Union[int, str]): Block height or hash (0x-prefixed string).

        Returns:
            BlockchainResponse: Standardized response containing block information.
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBlock",
            "params": [
                block_identifier,
                {
                    "encoding": "json",
                    "maxSupportedTransactionVersion": 0,
                    "transactionDetails": "full",  # 可选值：full/accounts/none
                    "rewards": False
                }
            ]
        }

        try:
            response = requests.post(
                self.rpc_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=10
            )
        
            if response.status_code == 200:
                data = response.json()
                content = f"""
                    blockTime: {data["result"]["blockTime"]},
                    blockHeight: {data["result"]["blockHeight"]},
                    blockhash: {data["result"]["blockhash"]},
                    parentSlot: {data["result"]["parentSlot"]},
                    previousBlockhash: {data["result"]["previousBlockhash"]},
                    transactions: {len(data["result"]["transactions"])}
                """
                return BlockchainResponse(success=True, data=content, error=None)
            else:
                print(f"请求失败，状态码：{response.status_code}")
                return BlockchainResponse(success=False, data=f"Get请求失败，状态码：{response.status_code}", error=None)
            
        except requests.exceptions.RequestException as e:
            print(f"网络异常：{str(e)}")
            return BlockchainResponse(success=False, data=None, error=e)
    
    def get_balance(self, address) -> BlockchainResponse:
        """
        Get the balance of a Solana address.

        Args:
            address (str): The Solana address to check.

        Returns:
            BlockchainResponse: Standardized response containing balance information.
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [address]
        }

        try:
            response = requests.post(
                self.rpc_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=10
            )
        
            if response.status_code == 200:
                data = response.json()
                balance = round(data["result"]["value"] / (10**9), 5)
                content = f"""
                    Balance: {balance} SOL
                """
                return BlockchainResponse(success=True, data=content, error=None)
            else:
                print(f"请求失败，状态码：{response.status_code}")
                return BlockchainResponse(success=False, data=f"Get请求失败，状态码：{response.status_code}", error=None)
            
        except requests.exceptions.RequestException as e:
            print(f"网络异常：{str(e)}")
            return BlockchainResponse(success=False, data=None, error=e)
              
    def get_transaction(self, tx_hash)-> BlockchainResponse:
        """
        Get transaction details for a given transaction hash.

        Args:
            tx_hash (str): The transaction hash to check.

        Returns:
            BlockchainResponse: Standardized response containing transaction information.
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [tx_hash]
        }

        try:
            response = requests.post(
                self.rpc_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=10
            )
        
            if response.status_code == 200:
                data = response.json()
                print(f"Transaction: {data}")
                content = f"""
                    Transaction: {data["result"]}
                """
                return BlockchainResponse(success=True, data=content, error=None)
            else:
                print(f"请求失败，状态码：{response.status_code}")
                return BlockchainResponse(success=False, data=f"Get请求失败，状态码：{response.status_code}", error=None)
            
        except requests.exceptions.RequestException as e:
            print(f"网络异常：{str(e)}")
            return BlockchainResponse(success=False, data=None, error=e)       
            
            
if __name__ == "__main__":
    # Example usage
    solana = SolanaBlockchain("https://api.mainnet-beta.solana.com")
    block_info = solana.get_block_info(330047999)
    print(block_info)
    # transaction_info = solana.get_transaction("2qCLFR5VHUWWGCMSmX29mymAW2efjVZG8gL4LYe7jWPeceneC7FyeX6asZj6bLFxrHbrgGx4VK3uepUwF9fhcRDz")
    # print(transaction_info)
    balance_info = solana.get_balance("3wf3Ttu4UhGC6ff1N7NVruXjdhsiP2CgPDMo4qhBApK9")
    print(balance_info)
    
    price_info = solana.get_price()
    print(price_info)