import re
import requests
from abc import abstractmethod
from typing import Union
from pydantic import field_validator
from blockchain_mcp.base import BaseBlockchain, BlockchainResponse


class BitcoinBlockchain(BaseBlockchain):
    def __init__(self, rpc_url: str, chain_id: int=0):
        super().__init__(rpc_url, chain_id)
        self.chain_name = "bitcoin"
        self.BTC_ADDRESS_PATTERN = re.compile(
            r'^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}$'  # 支持Legacy/SegWit/Bech32地址
        )
        
    def _rpc_call(self, method: str, params: list = []):
        """比特币核心JSON-RPC调用"""
        headers = {'content-type': 'application/json'}
        payload = {
            "jsonrpc": "1.0",
            "id": "curiosity",
            "method": method,
            "params": params
        }
        try:
            response = requests.post(
                self.rpc_url, 
                json=payload, 
                headers=headers,
                timeout=10
            ).json()
            return response.get('result')
        except Exception as e:
            return {"error": str(e)}

    def get_block_info(self, block_identifier: Union[int, str]) -> BlockchainResponse:
        """
        获取比特币区块信息[3,6](@ref)
        - 支持区块高度或哈希查询
        - 包含交易数量和Merkle根
        """
        try:
            if isinstance(block_identifier, int):
                block_hash = self._rpc_call("getblockhash", [block_identifier])
            else:
                block_hash = block_identifier
            
            block_info = self._rpc_call("getblock", [block_hash, 2])  # verbosity=2包含交易详情
            
            structured_data = {
                "hash": block_info["hash"],
                "height": block_info["height"],
                "timestamp": block_info["time"],
                "transaction_count": len(block_info["tx"]),
                "merkle_root": block_info["merkleroot"],
                "difficulty": block_info["difficulty"],
                "confirmations": block_info["confirmations"]
            }
            return BlockchainResponse(success=True, data=structured_data)
        except Exception as e:
            return BlockchainResponse(success=False, error=str(e))

    def get_transaction(self, tx_hash: str) -> BlockchainResponse:
        """
        获取比特币交易详情[3,10](@ref)
        - 解析UTXO模型的输入输出
        - 包含交易状态和确认数
        """
        try:
            tx_info = self._rpc_call("getrawtransaction", [tx_hash, True])
            block_hash = tx_info.get("blockhash", "")
            confirmations = tx_info.get("confirmations", 0)
            
            # 解析输入输出
            inputs = [{
                "address": inp.get("prevout", {}).get("scriptPubKey", {}).get("address"),
                "value": inp.get("prevout", {}).get("value")
            } for inp in tx_info.get("vin", [])]
            
            outputs = [{
                "address": out["scriptPubKey"]["addresses"][0],
                "value": out["value"]
            } for out in tx_info.get("vout", [])]
            
            structured_data = {
                "txid": tx_info["txid"],
                "inputs": inputs,
                "outputs": outputs,
                "fee": sum(inp["value"] for inp in inputs) - sum(out["value"] for out in outputs),
                "block_hash": block_hash,
                "confirmations": confirmations,
                "status": "confirmed" if confirmations > 6 else "pending"
            }
            return BlockchainResponse(success=True, data=structured_data)
        except Exception as e:
            return BlockchainResponse(success=False, error=str(e))

    def get_balance(self, address: str) -> BlockchainResponse:
        """
        查询比特币地址余额[3,9](@ref)
        - 基于UTXO模型计算未花费输出
        - 支持多种地址格式验证
        """
        if not self.BTC_ADDRESS_PATTERN.match(address):
            return BlockchainResponse(
                success=False, 
                error="Invalid Bitcoin address format"
            )
        
        try:
            # 获取未花费交易输出
            utxos = self._rpc_call("listunspent", [0, 9999999, [address]])
            total_balance = sum(utxo["amount"] for utxo in utxos) * 1e8  # 转成satoshi单位
            return BlockchainResponse(
                success=True,
                data={
                    "address": address,
                    "confirmed": total_balance,
                    "unconfirmed": 0,  # 比特币需要单独处理未确认余额
                    "unit": "satoshi"
                }
            )
        except Exception as e:
            return BlockchainResponse(success=False, error=str(e))

    @field_validator('chain_id')
    def validate_chain_id(cls, v):
        """比特币主网chain_id固定为0"""
        if v != 0:
            raise ValueError("Bitcoin chain_id must be 0")
        return v