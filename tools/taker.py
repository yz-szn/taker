import json
import time
import requests
import os
from web3 import Web3
from eth_account.messages import encode_defunct
from utils.logger import log

API_URL = "https://lightmining-api.taker.xyz/"
HEADERS = {"Content-Type": "application/json"}
PROVIDER_URL = "https://rpc-mainnet.taker.xyz/"
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

web3 = Web3(Web3.HTTPProvider(PROVIDER_URL))
if not web3.is_connected():
    log("TakerBOT", "Failed to connect to Ethereum node.", "ERROR")
    exit(1)

def read_wallets():
    try:
        with open(os.path.join("data", "wallets.json"), "r") as file:
            wallets = json.load(file)
            if not wallets:
                log("TakerBOT", "No wallets found in wallets.json. Exiting...", "ERROR")
                exit(1)
            return wallets
    except FileNotFoundError:
        log("TakerBOT", "File wallets.json not found. Exiting...", "ERROR")
        exit(1)

def get(url, token=None, retries=3):
    headers = HEADERS.copy()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for _ in range(retries):
        try:
            response = requests.get(API_URL + url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            log("TakerBOT", f"GET request failed: {e}. Retrying...", "ERROR")
            time.sleep(3)
    return None

def post(url, data, token=None, retries=3):
    headers = HEADERS.copy()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for _ in range(retries):
        try:
            response = requests.post(API_URL + url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            log("TakerBOT", f"POST request failed: {e}. Retrying...", "ERROR")
            time.sleep(3)
    return None

def sign_message(message, private_key):
    try:
        encoded_message = encode_defunct(text=message)
        signed_message = web3.eth.account.sign_message(encoded_message, private_key=private_key)
        return signed_message.signature.hex()
    except Exception as e:
        log("TakerBOT", f"Error signing message: {e}", "ERROR")
        return None

def get_nonce(wallet_address):
    response = post("wallet/generateNonce", {"walletAddress": wallet_address})
    if response and "data" in response and "nonce" in response["data"]:
        return response["data"]["nonce"]
    log("TakerBOT", "Failed to get nonce.", "ERROR")
    return None

def login(address, message, signature):
    response = post("wallet/login", {
        "address": address,
        "invitationCode": "M3XT6",
        "message": message,
        "signature": signature,
    })
    if response and "data" in response and "token" in response["data"]:
        return response["data"]["token"]
    log("TakerBOT", "Failed to login.", "ERROR")
    return None

def get_user(token):
    response = get("user/getUserInfo", token)
    if response and "data" in response:
        user_data = response["data"]
        log("TakerBOT", f"UserID : {user_data.get('userId', 'N/A')}", "INFO")
        log("TakerBOT", f"Wallet Address : {user_data.get('walletAddress', 'N/A')}", "INFO")
        log("TakerBOT", f"Reward Amount : {user_data.get('rewardAmount', 'N/A')}", "INFO")
        log("TakerBOT", f"Invite Count : {user_data.get('inviteCount', 'N/A')}", "INFO")
        log("TakerBOT", f"Invitation Reward : {user_data.get('invitationReward', 'N/A')}", "INFO")
        log("TakerBOT", f"Total Reward : {user_data.get('totalReward', 'N/A')}", "INFO")
        log("TakerBOT", f"Twitter : {user_data.get('twName', 'N/A')}", "INFO")
        return user_data
    log("TakerBOT", "Failed to get user info.", "ERROR")
    return None

def get_miner_status(token):
    response = get("assignment/totalMiningTime", token)
    if response and "data" in response:
        return response["data"]
    log("TakerBOT", "Failed to get miner status.", "ERROR")
    return None

def start_mine(token):
    response = post("assignment/startMining", {}, token)
    if response:
        return response
    log("TakerBOT", "Failed to start mining.", "ERROR")
    return None

def activate_mining(private_key):
    try:
        wallet = web3.eth.account.from_key(private_key)
        contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

        nonce = web3.eth.get_transaction_count(wallet.address, 'pending')
        gas = contract.functions.active().estimate_gas({'from': wallet.address})
        gas_price = web3.eth.gas_price

        tx = contract.functions.active().build_transaction({
            "from": wallet.address,
            "gas": gas,
            "gasPrice": gas_price,
            "nonce": nonce,
        })

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        log("TakerBOT", f"Transaction confirmed. Hash: {tx_hash.hex()}", "INFO")
        return tx_hash.hex()
    except Exception as e:
        log("TakerBOT", f"Activate Mining Error: {e}", "ERROR")
        return None

def main():
    wallets = read_wallets()
    total_wallets = len(wallets)
    processed_wallets = 0
    skipped_wallets = 0

    log("TakerBOT", f"Starting processing all wallets: {total_wallets}", "INFO")

    while True:
        for wallet in wallets:
            address = wallet["address"]
            private_key = wallet["privateKey"]

            nonce = get_nonce(address)
            if not nonce:
                skipped_wallets += 1
                continue

            signature = sign_message(nonce, private_key)
            if not signature:
                skipped_wallets += 1
                continue

            log("TakerBOT", f"Trying to login for wallet: {address}", "INFO")
            token = login(address, nonce, signature)
            if not token:
                skipped_wallets += 1
                continue
            log("TakerBOT", "Login successful", "INFO")

            user_data = get_user(token)
            if user_data:
                if not user_data.get("twName"):
                    log("TakerBOT", f"Wallet {address} is not bound to Twitter/X. Skipping...", "ERROR")
                    skipped_wallets += 1
                    continue

            miner_status = get_miner_status(token)
            if miner_status:
                last_mining_time = miner_status.get("lastMiningTime", 0)
                next_mining_time = last_mining_time + 24 * 60 * 60
                next_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(next_mining_time))
                log("TakerBOT", f"Last mining time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_mining_time))}", "INFO")
                if time.time() > next_mining_time:
                    log("TakerBOT", f"Trying to start mining for wallet: {address}", "INFO")
                    mine_response = start_mine(token)
                    if mine_response:
                        log("TakerBOT", "Mining started. Activating on-chain...", "INFO")
                        tx_hash = activate_mining(private_key)
                        if tx_hash:
                            log("TakerBOT", f"Activate Mining confirmed. Hash: {tx_hash}", "INFO")
                            processed_wallets += 1
                        else:
                            log("TakerBOT", "Failed to activate mining on-chain.", "ERROR")
                            skipped_wallets += 1
                    else:
                        log("TakerBOT", "Failed to start mining.", "ERROR")
                        skipped_wallets += 1
                else:
                    log("TakerBOT", f"Mining already started. Next mining time: {next_date}", "WARN")
                    skipped_wallets += 1
            else:
                log("TakerBOT", "Failed to get miner status.", "ERROR")
                skipped_wallets += 1

        log("TakerBOT", f"Total wallets: {total_wallets}, Processed: {processed_wallets}, Skipped: {skipped_wallets}", "INFO")
        log("TakerBOT", "All wallets processed. Cooling down for 1 hour...", "INFO")
        time.sleep(60 * 60)

if __name__ == "__main__":
    main()
