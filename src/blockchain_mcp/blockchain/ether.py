from web3 import Web3, AsyncWeb3

class Ether:
    def __init__(self, url):
        self.w3 = Web3(Web3.HTTPProvider(url))


    def get_block_info(self, block_num)->str:
        """Get latest Ethereum block information

        Returns:
            dict: A dictionary of block information
        """
        block_info = self.w3.eth.get_block(block_num).__dict__
        return f"""
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
        
    def get_balance(self, addr)->dict:
        """Get balance of address

        Args:
            addr (_type_): _description_

        Returns:
            dict: _description_
        """
        

if __name__ == "__main__":
    eth = Ether('https://mainnet.infura.io/v3/8cbcfeeded8046f3a4d4fbd0c913f62c')
    print(eth.get_block_info("latest"))