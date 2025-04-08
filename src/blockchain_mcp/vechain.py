import os
import re
from typing import Union

import requests

from blockchain_mcp.base import BlockchainResponse, BaseBlockchain


class Vechain(BaseBlockchain):
    """
    Vechain区块链类
    """
    def __init__(self, url: str):
        super().__init__(url, 42)
        self.chain_name = "vechain"
        self.session = requests.Session()
        
        # 配置默认请求头
        self.headers = {
            'Accept': 'application/json, text/plain',
            'User-Agent': 'Vechain-Client/1.0'
        }
        
    def get_block_info(self, block_identifier: Union[int, str])->BlockchainResponse:
        """
        获取Vechain区块信息
        :param block_identifier: 区块高度或哈希（0x开头字符串）
        :return: 包含区块哈希、时间戳、交易根等数据的标准化响应
        """
        try:
            self._validate_block_identifier(block_identifier)
            url = f"{self.rpc_url}/blocks/{block_identifier}"
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            
            block_info = response.json()
            if block_info is None:
                return BlockchainResponse(success=True, data="Block not found", error=None)
            
            data = f"""
                id: {block_info["id"]},
                parentID: {block_info["parentID"]},
                number: {block_info["number"]},
                size: {block_info["size"]},
                timestamp: {block_info["timestamp"]},
                beneficiary: {block_info["beneficiary"]},
                gasUsed: {block_info["gasUsed"]},
                gasLimit: {block_info["gasLimit"]},
                stateRoot: {block_info["stateRoot"]},
                receiptsRoot: {block_info["receiptsRoot"]},
                signer: {block_info["signer"]},
                txsFeatures: {block_info["txsFeatures"]},
                isTrunk: {block_info["isTrunk"]},
                isFinalized: {block_info["isFinalized"]},
                transactions:{block_info["transactions"]}
            """
            return BlockchainResponse(success=True, data=data, error=None)
        except requests.HTTPError as e:
            print(f"Get block info error: {str(e)}")
            if e.response.status_code == 400:
                return BlockchainResponse(success=True, data="Block Id is not valid", error=str(e))
            else:
                return BlockchainResponse(success=False, data=None, error=str(e))
        except requests.RequestException as e:
            print(f"Get block info error: {str(e)}")
            return BlockchainResponse(success=False, data=None, error=str(e))
    
    def get_transaction(self, tx_id: str) -> BlockchainResponse:
        """
        获取Vechain交易详情
        :param tx_id: 交易哈希（0x开头字符串）
        :return: 包含交易金额、发送方、接收方、状态等信息的标准化响应
        """
        try:
            self._validate_tx_hash(tx_hash=tx_id)
            url = f"{self.rpc_url}/transactions/{tx_id}"
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            transaction_info = response.json()
            if transaction_info is None:
                data = "Transaction not found"
                return BlockchainResponse(success=True, data=data, error=None)
            else:
                data = f"""
                    id: {transaction_info["id"]},
                    chainTag: {transaction_info["chainTag"]},
                    blockRef: {transaction_info["blockRef"]},
                    expiration: {transaction_info["expiration"]},
                    gasPriceCoef: {transaction_info["gasPriceCoef"]},
                    gas: {transaction_info["gas"]},
                    nonce: {transaction_info["nonce"]},
                    origin: {transaction_info["origin"]},
                    delegator: {transaction_info["delegator"]},
                    dependsOn: {transaction_info["dependsOn"]},
                    size: {transaction_info["size"]},
                    clauses: {transaction_info["clauses"]},
                    meta: {transaction_info["meta"]}
                """    
                return BlockchainResponse(success=True, data=data, error=None)
        except requests.HTTPError as e:
            print(f"Get transaction error: {str(e)}")
            if e.response.status_code == 400:
                return BlockchainResponse(success=True, data="Transaction not found", error=str(e))
            else:
                return BlockchainResponse(success=False, data=None, error=str(e))
        except requests.RequestException as e:
            print(f"Get transaction error: {str(e)}")
            return BlockchainResponse(success=False, data=None, error=str(e))
        except ValueError as e:
            print(f"Error: {str(e)}")
            return BlockchainResponse(success=False, data=None, error=str(e))
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return BlockchainResponse(success=False, data=None, error=str(e))
           
    
    def get_balance(self, address: str) -> BlockchainResponse:
        """
        获取Vechain地址余额
        :param address: 支持Vechain地址（0x前缀）
        :return: 包含余额信息的标准化响应
        """
        try:
            self._validate_address(address=address)
            url = f"{self.rpc_url}/accounts/{address}"
            print(f"url:{url}")
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            balance_info = response.json()
            data = f"""
                Balance:{Vechain.hex_to_decimal(balance_info['balance'])} VET
                Energe:{Vechain.hex_to_decimal(balance_info['energy'])} VTHO
                HasCode:{balance_info['hasCode']}
            """
            return BlockchainResponse(success=True, data=data, error=None)
        except requests.HTTPError as e:
            print(f"Get balance error: {str(e)}")
            if e.response.status_code == 400:
                return BlockchainResponse(success=True, data="Invalid address", error=str(e))
            else:
                return BlockchainResponse(success=False, data=f"Get balance error: {str(e)}", error=str(e))
        except requests.RequestException as e:
            print(f"Get balance error: {str(e)}")
            return BlockchainResponse(success=False, data=f"Get balance error: {str(e)}", error=str(e))
        except ValueError as e:
            print(f"Error: {str(e)}")
            return BlockchainResponse(success=False, data=f"Error: {str(e)}", error=str(e))
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return BlockchainResponse(success=False, data=f"Unexpected error: {str(e)}", error=str(e))
    
    @staticmethod
    def hex_to_decimal(hex_str: str, divisor: int = 10**18) -> float:
        decimal_value = int(hex_str, 16)
        return round(decimal_value / divisor, 5)
     
    def _validate_block_identifier(self, block_identifier: Union[int, str]):
        if isinstance(block_identifier, int):
            if block_identifier < 0:
                raise ValueError("Block identifier must be a non-negative integer")
        elif isinstance(block_identifier, str):
            if block_identifier == "best":
                return 
            elif not re.match(r'^(0x)?[0-9a-fA-F]{64}$', block_identifier):
                raise ValueError("Block identifier must be an integer or string")
    def _validate_address(self, address):
        
        if not re.match(r'^(0x)?[0-9a-fA-F]{40}$', address):
            raise ValueError("Invalid Vechain address format")
    
    def _validate_tx_hash(self, tx_hash: str) -> bool:
        """Validate transaction hash format"""
        if not isinstance(tx_hash, str):
            raise ValueError("Vechain Tx Id must be string")
        if not re.match(r'^(0x)?[0-9a-fA-F]{64}$', tx_hash):
            raise ValueError("Vachain Invalid tx Id format")    
    
           
if __name__ == "__main__":
    VECHAIN_NODE_URL = os.getenv("VECHAIN_NODE_URL")
    vechain = Vechain(VECHAIN_NODE_URL)
    # print(vechain.get_block_info("best"))
    # print(vechain.get_balance("0x1234567890abcdef1234567890abcdef12345678"))
    #print(vechain.get_transaction("0x1c31133a632433cd4896c6303a562926eb84378356dee33484ebf6b72391daed"))
    print(vechain.get_price())