from decimal import Decimal
from fastmcp import FastMCP
from typing import Optional, Union
import jsonschema
from blockchain_mcp.chains_factory import GetBlockChain

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
                "pattern": "^[latest|best]$",
                "description": "Block number（number or 'latest'or 'best'）"
            }
        },
        "required": ["blockchain_name"],
        "additionalProperties": false
    }
    """

    if block_number is None:
        block_number = "latest"
        
    print("Parameters: %s, %s"%(blockchain_name, block_number))
    try:
        bc = GetBlockChain(blockchain_name)
        return bc.get_block_info(block_number)
    except ValueError as ve:
        return f"ValueError: {str(ve)}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_balance(blockchain_name: str,address: str) -> dict:
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
        bc = GetBlockChain(blockchain_name)
        trimed_address = address.strip()
        balance = bc.get_balance(trimed_address)
        return balance
    except ValueError as ve:
        return f"ValueError: {str(ve)}"
    except Exception as e:
        return f"Error: {str(e)}"
    
@mcp.tool()
def get_transaction(blockchain_name:str, tx_hash:str) -> dict:
    """
    获取区块链交易详情（自动处理地址格式）
    
    参数 Schema：
    {
        "type": "object",
        "properties": {
            "blockchain_name": {
                "type": "string",
                "enum": ["bitcoin", "ethereum", "vechain", "solana"],
                "description": "区块链类型（不区分大小写）"
            },
            "tx_hash": {
                "type": "string",
                "description": "有效的区块链交易哈希"
            }
        },
        "required": ["blockchain_name", "tx_hash"]
    }
    """
    try:
        # 获取原始交易详情
        bc = GetBlockChain(blockchain_name)
        trimed_tx_hash = tx_hash.strip()
        transaction = bc.get_transaction(trimed_tx_hash)
        return transaction
    except ValueError as ve:
        return f"ValueError: {str(ve)}"
    except TypeError as te:
        return f"TypeError: {str(te)}"
    except Exception as e:
        return f"Error: {str(e)}"
 
@mcp.tool()
def get_price(blockchain_name: str) -> dict:
    """
    获取区块链当前价格（主网代币）
    
    参数 Schema：
    {
        "type": "object",
        "properties": {
            "blockchain_name": {
                "type": "string",
                "enum": ["bitcoin", "ethereum", "vechain", "solana"],
                "description": "区块链类型（不区分大小写）"
            }
        },
        "required": ["blockchain_name"]
    }
    """
    try:
        # 获取原始价格
        bc = GetBlockChain(blockchain_name)
        price = bc.get_price()
        return price
    except ValueError as ve:
        return f"ValueError: {str(ve)}"
    except Exception as e:
        return f"Error: {str(e)}"
    
# 生成 Claude 提示模板（网页7动态发现机制）
def generate_tool_prompt() -> str:
    return f"""
    ## 可用工具：
    # get_blockchain_info
    - 功能：查询区块链最新区块信息
    - 参数规范：
      {{
        "blockchain_name": "区块链名称（必填，可选：Ethereum/Bitcoin/Vechain/Solana）",
        "block_number": "区块编号（可选，默认'latest'）"
      }}
    - 示例请求（网页4提示语工程）：
      用户输入："获取以太坊最新区块"
      → 生成参数：{{"blockchain_name": "Ethereum", "block_number": "latest"}}
    get_transaction
    - 功能：查询区块链交易详情
    - 参数规范：
      {{
        "blockchain_name": "区块链名称（必填，可选：Ethereum/Bitcoin/Vechain/Solana）",
        "tx_hash": "交易哈希（必填）"
      }}
    - 示例请求（网页4提示语工程）：
      用户输入："获取以太坊交易详情"
      → 生成参数：{{"blockchain_name": "Ethereum", "tx_hash": "0x1234567890abcdef"}}
    get_balance
    - 功能：查询区块链地址余额 
    - 参数规范：
      {{
        "blockchain_name": "区块链名称（必填，可选：Ethereum/Bitcoin/Vechain/Solana）",
        "address": "地址（必填）"
      }}
    - 示例请求（网页4提示语工程）：
      用户输入："获取以太坊地址余额"
      → 生成参数：{{"blockchain_name": "Ethereum", "address": "0x1234567890abcdef"}}
    """
 
def main():
    print("Start blockchain mcp server.")
    mcp.run()