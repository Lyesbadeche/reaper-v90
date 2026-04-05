import requests
import time
import re
import json
import os

# --- [V91.0: THE SOVEREIGN OMNI-REAPER] | THE WHALE-HUNTER LIVE EDITION ---

class OmniReaperWhaleHunter:
    def __init__(self, api_keys, tg_token=None, tg_id=None):
        self.keys = api_keys
        self.tg_token = tg_token
        self.tg_id = tg_id
        self.networks = {
            "ETH": "https://api.etherscan.io/api",
            "BSC": "https://api.bscscan.com/api",
            "POLYGON": "https://api.polygonscan.com/api"
        }
        self.vulnerabilities_log = []
        self.total_scanned = 0
        self.scanned_addresses = set()

    def get_contract_data(self, chain, address):
        url = self.networks[chain]
        key = self.keys.get(chain)
        if not key: return None, 0

        try:
            # 1. Verify if address is a contract
            code_params = {"module": "proxy", "action": "eth_getCode", "address": address, "apikey": key}
            code_res = requests.get(url, params=code_params).json()
            bytecode = code_res.get('result', '0x')
            
            if len(bytecode) < 50: return None, 0 # Skip EOAs and tiny contracts

            # 2. Check Real Liquidity (Balance)
            bal_params = {"module": "account", "action": "balance", "address": address, "apikey": key}
            bal_res = requests.get(url, params=bal_params).json()
            balance_wei = int(bal_res.get('result', '0'))
            balance_eth = balance_wei / 1e18
            
            # Simple USD conversion
            price = 3500 if chain == "ETH" else 600 if chain == "BSC" else 1
            usd_value = balance_eth * price
            
            return bytecode, usd_value
        except:
            return None, 0

    def _decompile_bytecode_logic(self, bytecode):
        # Critical function signatures
        dangerous_signatures = {
            "0xa9059cbb": "Transfer Function",
            "0x23b872dd": "TransferFrom (Drain Risk)",
            "0xde5f8566": "DelegateCall (Hijack Risk)"
        }
        found_logic = []
        for sig, name in dangerous_signatures.items():
            if sig in bytecode:
                found_logic.append(name)
        return found_logic

    def _audit_engine_v91(self, chain, address, bytecode, usd_value):
        # MINIMUM LIQUIDITY FILTER ($10.00)
        if usd_value < 10: return False

        findings = self._decompile_bytecode_logic(bytecode)
        
        # STOP VANITY SPAM (eeee/ffff)
        if address.lower().endswith("eeeeeeeeee") or address.lower().endswith("ffffffffff"):
            return False

        if findings:
            for f in findings:
                msg = f"[{chain}] {f} | 💰 BOUNTY: ${usd_value:,.2f} | ADDR: `{address}`"
                self.send_telegram_alert(msg)
            return True
        return False

    def send_telegram_alert(self, message):
        if not self.tg_token or not self.tg_id: return
        url = f"https://api.telegram.org/bot{self.tg_token}/sendMessage"
        payload = {"chat_id": self.tg_id, "text": f"🚨 [LIVE TARGET FOUND]\n{message}", "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload, timeout=5)
        except:
            pass

    def RUN_SUPREME_HUNT(self):
        print("--- 📡 V91.0 OMNI-REAPER | REAL-TIME SCANNER ACTIVE ---")
        try:
            while True:
                for chain, api_url in self.networks.items():
                    key = self.keys.get(chain)
                    if not key: continue
                    
                    try:
                        # Fetch the latest block transactions
                        params = {
                            "module": "proxy",
                            "action": "eth_getBlockByNumber",
                            "tag": "latest",
                            "boolean": "true",
                            "apikey": key
                        }
                        response = requests.get(api_url, params=params, timeout=10).json()
                        txs = response.get('result', {}).get('transactions', [])
                        
                        for tx in txs[:20]: # Scan first 20 txs in block
                            target = tx.get('to')
                            if not target or target in self.scanned_addresses: continue
                            
                            self.scanned_addresses.add(target)
                            self.total_scanned += 1
                            
                            bytecode, usd_val = self.get_contract_data(chain, target)
                            if bytecode:
                                self._audit_engine_v91(chain, target, bytecode, usd_val)
                            
                    except Exception as e:
                        print(f"Error: {e}")
                    
                    time.sleep(5) # API Rate Limit protection
                
                if len(self.scanned_addresses) > 2000:
                    self.scanned_addresses.clear()
                    
                print(f"[STATUS] Total Real Audits: {self.total_scanned}")
        except KeyboardInterrupt:
            print("\n[!] Hibernating.")

if __name__ == "__main__":
    KEYS = {
        "ETH": os.getenv("ETHERSCAN_KEY"),
        "BSC": os.getenv("BSCSCAN_KEY"),
        "POLYGON": os.getenv("POLYGONSCAN_KEY")
    }
    reaper = OmniReaperWhaleHunter(
        KEYS, 
        os.getenv("TELEGRAM_TOKEN"), 
        os.getenv("TELEGRAM_CHAT_ID")
    )
    reaper.RUN_SUPREME_HUNT()
