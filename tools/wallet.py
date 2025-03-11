import json
import os
from utils.logger import log

def convert_wallet_to_json(input_file, output_file):
    wallets = []
    
    try:
        with open(input_file, 'r') as file:
            lines = file.readlines()
        for line in lines:
            line = line.strip()
            if ':' in line:
                address, private_key = line.split(':', 1)
                wallets.append({"address": address, "private_key": private_key})
        
        with open(output_file, 'w') as json_file:
            json.dump(wallets, json_file, indent=2)
        
        log("Wallet Converter", f"Berhasil membuat {output_file} dengan format JSON!", "SUCCESS")
    except Exception as e:
        log("Wallet Converter", f"Terjadi kesalahan: {e}", "ERROR")

def run():
    input_file = os.path.join("data", "wallet.txt")
    output_file = os.path.join("data", "wallets.json")
    convert_wallet_to_json(input_file, output_file)
if __name__ == "__main__":
    run()
