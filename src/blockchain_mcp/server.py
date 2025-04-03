import datetime
from fastmcp import FastMCP
from typing import Optional, Union
import jsonschema
from . import blockchain
from .blockchain import BaseBlockchain

mcp = FastMCP("BlockchainMCP", dependencies=["mcp[cli]", "web3"])


@mcp.tool()
def get_blockchain_info(
    blockchain_name: str,
    block_number: Optional[Union[int, str]] = "latest"
) -> dict:
    """
    Get specified block information
    
    Parameters Schema definition
    {
        "type": "object",
        "properties": {
            "blockchain_name": {
                "type": "string",
                "enum": ["ethereum", "bitcoin", "vechain"],
                "description": "Blockchain name"
            },
            "block_number": {
                "type": ["integer", "string"],
                "pattern": "^latest$",
                "description": "Block number（number or 'latest'）"
            }
        },
        "required": ["blockchain_name"],
        "additionalProperties": false
    }
    """

    if block_number is None:
        block_number = "latest"
        
     # 预处理区块链名称（网页2大小写处理方案）
    formatted_name = blockchain_name.strip().lower().capitalize()
    
    # 验证区块链名称
    valid_chains = ["Bitcoin", "Ethereum", "Vechain", "Solana"]
    if formatted_name not in valid_chains:
        raise ValueError(f"不支持的区块链: {formatted_name}，请选择 {valid_chains}")
    
    block_num = validate_block_number(block_number)
        
    print("Parameters: %s, %s"%(blockchain_name, block_num))
    bc = blockchain.GetBlockChain(blockchain_name)
    return bc.get_block_info(block_num)
    

@mcp.tool()
def get_balance(params: BalanceRequest) -> dict:
    """
    获取区块链地址余额（自动处理地址格式，保留5位小数）
    
    参数 Schema：
    {
        "type": "object",
        "properties": {
            "blockchain_name": {
                "type": "string",
                "enum": ["bitcoin", "ethereum", "vechain", "solana"],
                "description": "区块链类型（不区分大小写）"
            },
            "address": {
                "type": "string",
                "description": "有效的区块链地址"
            }
        },
        "required": ["blockchain_name", "address"]
    }
    """
    try:
        # 获取原始余额
        raw_balance = _get_raw_balance(params.blockchain_name, params.address)
        
        # 单位转换与精度处理
        divisor = {
            "bitcoin": Decimal(10**8),
            "ethereum": Decimal(10**18),
            "vechain": Decimal(10**18),
            "solana": Decimal(10**9)
        }[params.blockchain_name]

        balance = Decimal(raw_balance) / divisor
        return str(balance.quantize(Decimal('0.00000'), rounding=ROUND_HALF_UP))
    
    except Exception as e:
        return f"Error: {str(e)}"
    

 
def validate_block_number(value):
    validation_schema = {
        "block_number": {
            "anyOf": [
                {"type": "integer", "minimum": 0},
                {"const": "latest"}
            ]
        }
    }
    try:
        jsonschema.validate(instance={"block_number": value}, schema=validation_schema)
    except jsonschema.ValidationError as e:
        raise ValueError(f"无效的区块编号: {e.message}")
    # 统一转为小写处理（网页2大小写规范）
    if isinstance(value, str):
        value = value.strip().lower()
        if value == "latest":
            return "latest"
        elif value.isdigit():
            return int(value)
    return value

    
# 生成 Claude 提示模板（网页7动态发现机制）
def generate_tool_prompt() -> str:
    return f"""
    ## 可用工具：get_blockchain_info
    - 功能：查询区块链最新区块信息
    - 参数规范：
      {{
        "blockchain_name": "区块链名称（必填，可选：Ethereum/Bitcoin/Vechain）",
        "block_number": "区块编号（可选，默认'latest'）"
      }}
    - 示例请求（网页4提示语工程）：
      用户输入："获取以太坊最新区块"
      → 生成参数：{{"blockchain_name": "Ethereum", "block_number": "latest"}}
    """

def _get_raw_balance(blockchain_name, address):
    if blockchain_name.lower() == 'ethereum':
        
    elif blockchain_name.lower() == 'vechain':
        pass
    elif blockchain_name.lower() == 'solana':
        pass
    elif blockchain_name.lower() == 'bitcoin':
        pass

def _get_blockchain(blockchain_name):
    if blockchain_name.lower() == 'ethereum':
        return blockchain.ether.Ether(ETHEREUM_NODE_URL)
    elif blockchain_name.lower() == 'vechain':
        pass
    elif blockchain_name.lower() == 'solana':
        pass
    elif blockchain_name.lower() == 'bitcoin':
        pass  
def main():
    print("Start blockchain mcp server.")
    mcp.run()