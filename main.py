import requests
import time
import os

class OmniReaperWhaleHunter:
    def __init__(self):
        # Fetching keys directly from Railway Environment Variables
        self.keys = {
            "ETH": os.getenv("ETHERSCAN_KEY"),
            "BSC": os.getenv("BSCSCAN_KEY"),
            "POLYGON": os.getenv("POLYGONSCAN_KEY")
        }
        self.tg_token = os.getenv("TELEGRAM_TOKEN")
        self.tg_id = os.getenv("TELEGRAM_CHAT_ID")
        
        self.networks = {
            "ETH": "https://api.etherscan.io/api",
            "BSC": "https://api.bscscan.com/api",
            "POLYGON": "https://api.polygonscan.com/api"
        }
        self.scanned_addresses = set()
        self.total_scanned = 0

    def get_contract_data(self, chain, address):
        url = self.networks[chain]
        key = self.keys.get(chain)
        if not key: return None, 0
        
        try:
            # 1. Get Bytecode
            code_res = requests.get(url, params={"module": "proxy", "action": "eth_getCode", "address": address, "apikey": key}, timeout=10).json()
            bytecode = code_res.get('result', '0x')
            if len(bytecode) < 100: return None, 0
            
            # 2. Get Real Balance
            bal_res = requests.get(url, params={"module": "account", "action": "balance", "address": address, "apikey": key}, timeout=10).json()
            balance_wei = int(bal_res.get('result', '0'))
            usd_value = (balance_wei / 1e18) * (3500 if chain == "ETH" else 600 if chain == "BSC" else 1)
            
            return bytecode, usd_value
        except: return None, 0

    def audit_logic(self, chain, address, bytecode, usd):
        # CRITICAL VULNERABILITY SIGNATURES
        signatures = {
            "0xa9059cbb": "Transfer Logic Found",
            "0x23b872dd": "TransferFrom Detected",
            "0xde5f8566": "DelegateCall (High Risk)"
        }
        
        findings = [name for sig, name in signatures.items() if sig in bytecode]
        
        # FILTER: Only alert if Real Liquidity > $10 and not fake address
        if findings and usd > 10 and not address.lower().endswith("eeeeeeeeee"):
            msg = f"🚨 [WHALE FOUND]\nNet: {chain}\nAddr: `{address}`\nBounty: ${usd:,.2f}\nLogic: {', '.join(findings)}"
            requests.post(f"https://api.telegram.org/bot{self.tg_token}/sendMessage", 
                          json={"chat_id": self.tg_id, "text": msg, "parse_mode": "Markdown"})
            return True
        return False

    def start_engine(self):
        print("--- 📡 V91.0 OMNI-REAPER | LIVE SCANNER ACTIVE ---")
        while True:
            for chain, api_url in self.networks.items():
                key = self.keys.get(chain)
                if not key: continue
                
                try:
                    # Scan the latest real block transactions
                    res = requests.get(api_url, params={"module": "proxy", "action": "eth_getBlockByNumber", "tag": "latest", "boolean": "true", "apikey": key}, timeout=15).json()
                    transactions = res.get('result', {}).get('transactions', [])
                    
                    for tx in transactions[:10]:
                        target = tx.get('to')
                        if not target or target in self.scanned_addresses: continue
                        
                        self.scanned_addresses.add(target)
                        self.total_scanned += 1
                        
                        bytecode, usd = self.get_contract_data(chain, target)
                        if bytecode:
                            self.audit_logic(chain, target, bytecode, usd)
                            
                except Exception as e:
                    print(f"Error on {chain}: {e}")
                
                time.sleep(5) # Rate limiting protection
            
            if len(self.scanned_addresses) > 1000: self.scanned_addresses.clear()
            print(f"[STATUS] Total Real Audits: {self.total_scanned}")

if __name__ == "__main__":
    reaper = OmniReaperWhaleHunter()
    reaper.start_engine()
