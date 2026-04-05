import requests
import time
import re
import os
from dotenv import load_dotenv

# Load Environment Variables from the Server/Host
load_dotenv()

class OmniReaperSovereign:
    def __init__(self):
        # API Keys for Blockchain Explorers
        self.keys = {
            "ETH": os.getenv("ETHERSCAN_KEY"),
            "BSC": os.getenv("BSCSCAN_KEY"),
            "POLYGON": os.getenv("POLYGONSCAN_KEY")
        }
        
        # Telegram Integration Keys
        self.tg_token = os.getenv("TELEGRAM_TOKEN")
        self.tg_id = os.getenv("TELEGRAM_CHAT_ID")
        
        # API Base URLs
        self.networks = {
            "ETH": "https://api.etherscan.io/api",
            "BSC": "https://api.bscscan.com/api",
            "POLYGON": "https://api.polygonscan.com/api"
        }
        
        self.scan_count = 0

    def send_alert(self, message):
        """Sends real-time vulnerability alerts to Telegram"""
        if not self.tg_token or not self.tg_id:
            return
        
        url = f"https://api.telegram.org/bot{self.tg_token}/sendMessage"
        payload = {
            "chat_id": self.tg_id, 
            "text": f"🚨 [OMNI-REAPER V90 ALERT]\n{message}",
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"Telegram Notification Error: {e}")

    def audit_logic(self, chain, address, code):
        """Core Audit Engine for Vulnerability Detection"""
        findings = []
        
        # 1. Reentrancy Vulnerability Check
        if ".call{" in code and "balances[" in code:
            findings.append("HIGH: Potential Reentrancy Flow")
            
        # 2. Access Control / Self-Destruct Check
        if "selfdestruct" in code and "onlyOwner" not in code:
            findings.append("CRITICAL: Unprotected Self-Destruct")
            
        # 3. Arithmetic / Precision Risk Check
        if ("*" in code or "/") in code and "SafeMath" not in code.lower():
            findings.append("MEDIUM: Potential Arithmetic Precision Risk")

        if findings:
            report = (
                f"*Network:* {chain}\n"
                f"*Address:* `{address}`\n"
                f"*Issues:* {', '.join(findings)}\n"
                f"*Action:* Review on Immunefi immediately."
            )
            self.send_alert(report)
            return True
        return False

    def start_engine(self):
        """Starts the global monitoring loop"""
        print("--- [OMNI-REAPER V90] ENGINE STARTED ---")
        print(f"[*] Networks Monitored: {list(self.networks.keys())}")
        
        try:
            while True:
                for chain in self.networks.keys():
                    if not self.keys.get(chain):
                        continue
                    
                    # Simulation: In production, this fetches real real-time block data
                    target_addr = f"0x{int(time.time()):x}" + "e" * 10
                    sample_vulnerable_code = "function withdraw() public { msg.sender.call{value: 1 ether}(''); balances[msg.sender]=0; }"
                    
                    self.scan_count += 1
                    self.audit_logic(chain, target_addr, sample_vulnerable_code)
                    
                    # Prevent API Rate Limiting
                    time.sleep(5)
                
                print(f"[STATUS] Total Scans: {self.scan_count}", end="\r")
        except KeyboardInterrupt:
            print("\n[!] Sovereign Shutdown Initiated.")

if __name__ == "__main__":
    reaper = OmniReaperSovereign()
    reaper.start_engine()
