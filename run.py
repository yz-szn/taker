import os
import sys
import asyncio
from tools import wallet, taker
from utils.logger import log
from colorama import init, Fore, Style

init(autoreset=True)

def welcome():
    print(
        f"""
        {Fore.GREEN + Style.BRIGHT}
         /$$   /$$ /$$$$$$$$        /$$$$$$$ /$$$$$$$$ /$$$$$$$             
        | $$  | $$|____ /$$/       /$$_____/|____ /$$/| $$__  $$            
        | $$  | $$   /$$$$/       |  $$$$$$    /$$$$/ | $$  \ $$            
        | $$  | $$  /$$__/         \____  $$  /$$__/  | $$  | $$           
        |  $$$$$$$ /$$$$$$$$       /$$$$$$$/ /$$$$$$$$| $$  | $$           
         \____  $$|________/      |_______/ |________/|__/  |__/           
        /$$  | $$ ______________________________________________                                                     
       |  $$$$$$/ ============ Nothing's Impossible !! =========                                       
        \______/
        """
    )

welcome()
print(f"{Fore.CYAN}{'=' * 18}")
print(Fore.CYAN + "#### TakerBOT ####")
print(f"{Fore.CYAN}{'=' * 18}")

async def main():
    while True:
        print(Fore.YELLOW + "\n[=== PILIH MENU ===]")
        print(Fore.CYAN + "1. Convert Wallet")
        print(Fore.CYAN + "2. TakerBOT")
        print(Fore.CYAN + "3. Keluar")

        choice = input(Fore.GREEN + "Masukkan pilihan (1-3): ").strip()

        if choice == "1":
            log("Wallet Converter", "Memulai proses Convert...", "INFO")
            wallet.run() 
        elif choice == "2":
            log("TakerBOT", "Memulai proses TakerBOT...", "INFO")
            taker.main()
        elif choice == "3":
            log("TakerBOT", "Keluar dari program...", "INFO")
            return
        else:
            log("TakerBOT", "Pilihan tidak valid! Mohon pilih antara 1-3.", "ERROR")

if __name__ == "__main__":
    asyncio.run(main())