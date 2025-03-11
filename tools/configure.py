from web3 import Web3
from utils.logger import log

RPC_URL = "https://rpc-mainnet.taker.xyz/"
CONTRACT_ADDRESS = "0xB3eFE5105b835E5Dd9D206445Dbd66DF24b912AB"
CONTRACT_ABI = [
    {
        "constant": False,
        "inputs": [],
        "name": "active",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

w3 = Web3(Web3.HTTPProvider(RPC_URL))

def ca_rpc(private_key):
    try:
        account = w3.eth.account.from_key(private_key)
        contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

        tx = contract.functions.active().build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 200000,
            "gasPrice": w3.eth.gas_price
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        log("TakerBOT", f"Activate Mining confirmed Hash: {tx_hash.hex()}", "SUCCESS")

        return tx_hash.hex()
    except Exception as e:
        log("TakerBOT", f"Activate Mining Error: {str(e)}", "ERROR")
        return None
