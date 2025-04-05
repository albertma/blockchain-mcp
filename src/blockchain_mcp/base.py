# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Dict, Optional, Union
from pydantic import BaseModel, field_validator
import string
import re

class BlockchainResponse(BaseModel):
    success: bool
    data: Optional[Union[Dict, str]]
    error: Optional[str]

    
class BaseBlockchain(ABC):
    
    def __init__(self, rpc_url: str, chain_id: int):
      self.rpc_url = rpc_url
      self.chain_id = chain_id
      self.chain_name = "base"
      self.TX_HASH_PATTERN = re.compile(r'^(0x)?[0-9a-fA-F]{64}$')
    
    @abstractmethod
    def get_block_info(self, block_identifier: Union[int, str])->BlockchainResponse:
        """
        获取区块元数据（支持高度或哈希）

        Args:
            block_identifier (Union[int, str]): 区块高度（int）或哈希（0x开头字符串）

        Returns:
            BlockchainResponse: 包含区块哈希、时间戳、交易根等数据的标准化响应
        """
        pass
    
    @abstractmethod
    def get_balance(self, address: str) -> BlockchainResponse:
        """
        查询地址余额（主网代币）
        :param address: 支持EVM系地址（0x前缀）或其他链格式
        """
        pass
    
    @abstractmethod
    def get_transaction(self, tx_hash: str) -> BlockchainResponse:
        """
        获取交易详情（支持多链）
        :param tx_hash: 交易哈希（0x开头或比特币格式）
        :return: 包含交易金额、发送方、接收方、状态等信息的标准化响应
        """
        pass
    
    @field_validator('rpc_url')
    def validate_rpc(cls, v):
        """RPC端点格式校验"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("RPC URL必须以http/https开头")
        return v
    
    
    # def _validate_tx_hash(self, tx_hash: str) -> bool:
    #     if self.chain_name == "ethereum" or self.chain_name == "vechain":
    #         return bool(self.TX_HASH_PATTERN.fullmatch(tx_hash))
    #     elif self.chain_name == "bitcoin":
    #         # 比特币交易哈希无0x前缀
    #         return len(tx_hash) == 64 and all(c in string.hexdigits for c in tx_hash)
        
    # def _validate_address(self, address: str) -> bool:
    #     """地址格式校验"""
    #     if self.chain_name == "ethereum" or self.chain_name == "vechain":
    #         return bool(re.match(r'^0x[a-fA-F0-9]{40}$', address))
    #     elif self.chain_name == "bitcoin":
    #         # 比特币地址格式校验
    #         return bool(re.match(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', address))
    #     elif self.chain_name == "solana":
    #         # Solana 地址格式校验
    #         return bool(re.match(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$', address))
    #     return False