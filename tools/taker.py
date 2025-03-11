import json
import time
import requests
from eth_account import Account
from eth_account.messages import encode_defunct
from datetime import datetime
from utils.logger import log
from tools.configure import ca_rpc

API_BASE_URL = 'https://lightmining-api.taker.xyz/'

def read_wallets():
    try:
        with open("data/wallets.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        log("TakerBOT", "No wallets found in wallets.json", "ERROR")
        exit(1)

def make_request(method, endpoint, token=None, data=None, retries=3):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    url = f"{API_BASE_URL}{endpoint}"
    
    for attempt in range(retries):
        try:
            response = requests.request(method, url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            log("TakerBOT", f"Request failed ({method} {endpoint}): {str(e)}", "ERROR")
            if attempt < retries - 1:
                time.sleep(3)
    return None

def get(endpoint, token=None, retries=3):
    return make_request('GET', endpoint, token=token, retries=retries)

def post(endpoint, data=None, token=None, retries=3):
    return make_request('POST', endpoint, token=token, data=data, retries=retries)

def sign_message(message, private_key):
    try:
        message_encoded = encode_defunct(text=message)
        signed = Account.sign_message(message_encoded, private_key=private_key)
        return signed.signature.hex()
    except Exception as e:
        log("TakerBOT", f"Error signing message: {str(e)}", "ERROR")
        return None

def main():
    wallets = read_wallets()
    
    while True:
        log("TakerBOT", "=== Server might be slow - Please be patient ===", "WARN")
        log("TakerBOT", f"Processing {len(wallets)} wallets", "INFO")

        for wallet in wallets:
            address = wallet['address']
            private_key = wallet['private_key']

            # Get Nonce
            nonce_response = post('wallet/generateNonce', {'walletAddress': address})
            if not nonce_response or 'data' not in nonce_response:
                log("TakerBOT", f"Failed to get nonce for {address}", "ERROR")
                continue
            nonce = nonce_response['data'].get('nonce')

            # Sign Message
            signature = sign_message(nonce, private_key)
            if not signature:
                continue

            # Login
            login_data = {
                'address': address,
                'invitationCode': "M3XT6",
                'message': nonce,
                'signature': signature
            }
            login_response = post('wallet/login', login_data)
            if not login_response or 'data' not in login_response:
                log("TakerBOT", f"Login failed for {address}", "ERROR")
                continue
            
            token = login_response['data'].get('token')
            log("TakerBOT", f"Login successful for {address}", "SUCCESS")

            # Get User Info
            user_info = get('user/getUserInfo', token=token)
            if not user_info or 'data' not in user_info:
                log("TakerBOT", "Failed to get user info.", "ERROR")
                continue
            
            user_data = user_info['data']
            log("TakerBOT", f"UserID: {user_data.get('userId', 'N/A')}", "INFO")
            log("TakerBOT", f"Wallet Address: {user_data.get('walletAddress', 'N/A')}", "INFO")
            log("TakerBOT", f"Reward Amount: {user_data.get('rewardAmount', 'N/A')}", "INFO")
            log("TakerBOT", f"Invite Count: {user_data.get('inviteCount', 'N/A')}", "INFO")
            log("TakerBOT", f"Invitation Reward: {user_data.get('invitationReward', 'N/A')}", "INFO")
            log("TakerBOT", f"Total Reward: {user_data.get('totalReward', 'N/A')}", "INFO")
            log("TakerBOT", f"Twitter: {user_data.get('twName', 'N/A')}", "INFO")
            
            if not user_data.get('twName'):
                log("TakerBOT", f"Wallet {address} not bound to Twitter/X", "ERROR")
                continue

            # Mining Status
            miner_status = get('assignment/totalMiningTime', token=token)
            if miner_status and 'data' in miner_status:
                last_mine = miner_status['data'].get('lastMiningTime', 0)
                next_mine = last_mine + 86400  # 24 jam
                next_date = datetime.fromtimestamp(next_mine)
                
                if datetime.now() >= next_date:
                    mine_response = post('assignment/startMining', token=token)
                    if mine_response:
                        mining_success = ca_rpc(private_key)
                        if not mining_success:
                            log("TakerBOT", "On-chain mining failed", "ERROR")
                else:
                    log("TakerBOT", f"Next mining: {next_date.strftime('%Y-%m-%d %H:%M:%S')}", "WARN")

        log("TakerBOT", "Delay for 1 jam", "INFO")
        time.sleep(3600)

if __name__ == "__main__":
    main()
