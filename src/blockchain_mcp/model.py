from pydantic import BaseModel, Field, field_validator
from web3 import Web3
import re

class BalanceRequest(BaseModel):
    blockchain_name: str = Field(...,
        description="区块链类型（bitcoin/ethereum/vechain/solana）",
        examples=["ethereum", "BitCoin"])
    
    address: str = Field(...,
        description="区块链地址，支持带/不带0x前缀",
        examples=[
            "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
            "d3CdA913deB6f67967B99D67aCDFa1712C293601",
            "1Fh7ajXabJBpZPZw8bjD3QU4CuQ3pRty9u"
        ])

    @field_validator('blockchain_name')
    def normalize_blockchain(cls, v):
        v = v.strip().lower()
        if v not in ["bitcoin", "ethereum", "vechain", "solana"]:
            raise ValueError("仅支持 bitcoin/ethereum/vechain/solana")
        return v

    @field_validator('address')
    def normalize_address(cls, v, values):
        blockchain = values.get('blockchain_name', '').lower()
        
        # 以太坊系地址处理
        if blockchain in ["ethereum", "vechain"]:
            if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
                v = v if v.startswith("0x") else f"0x{v}"
            return Web3.to_checksum_address(v)
        
        # 比特币地址校验
        if blockchain == "bitcoin":
            patterns = [
                r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$',  # Legacy/SegWit
                r'^bc1[a-z0-9]{39,59}$'  # Bech32
            ]
            if not any(re.match(p, v) for p in patterns):
                raise ValueError("无效的比特币地址")
            return v
        
        # Solana 地址校验
        if blockchain == "solana":
            if not re.match(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$', v):
                raise ValueError("无效的Solana地址")
            return v