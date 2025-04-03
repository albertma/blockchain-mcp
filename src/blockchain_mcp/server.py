import datetime
from fastmcp import FastMCP
from typing import Optional, Union
import jsonschema
from . import blockchain

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
    if formatted_name == 'Ethereum':
        eth = blockchain.ether.Ether('https://mainnet.infura.io/v3/8cbcfeeded8046f3a4d4fbd0c913f62c')
        return eth.get_block_info(block_num)
    
    return {
        "blockchain": blockchain_name,
        "block_number": block_num if isinstance(block_num, int) else 19877365,
        "timestamp": datetime.datetime.now().isoformat(),
        "transactions": 215 if blockchain_name == "Ethereum" else 42
    }

 
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
    
def main():
    print("Start blockchain mcp server.")
    mcp.run()