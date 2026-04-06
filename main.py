import os
import asyncio
import requests
import subprocess
import sqlite3
import psycopg2
import redis
from flask import Flask, jsonify, render_template
from web3 import Web3
from transformers import pipeline
import ray

ray.init(ignore_reinit_error=True)

app = Flask(__name__)

class AdvancedAIAnalyzer:
    def __init__(self):
        self.nlp = pipeline("text-classification", model="distilbert-base-uncased")

    def analyze(self, bytecode):
        result = self.nlp(bytecode[:200])
        label = result[0]['label']
        score = result[0]['score']
        return label, score

class OmniReaperProScanner:
    def __init__(self):
        self.networks = {
            "ETH": Web3(Web3.HTTPProvider(os.getenv("ETH_RPC"))),
            "BSC": Web3(Web3.HTTPProvider(os.getenv("BSC_RPC"))),
            "POLYGON": Web3(Web3.HTTPProvider(os.getenv("POLYGON_RPC")))
        }
        self.tg_token = os.getenv("TELEGRAM_TOKEN")
        self.tg_id = os.getenv("TELEGRAM_CHAT_ID")
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK")
        self.slack_webhook = os.getenv("SLACK_WEBHOOK")
        self.email_api = os.getenv("EMAIL_API")

        self.conn = sqlite3.connect("scanner_results.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS results (
                                chain TEXT,
                                address TEXT,
                                balance REAL,
                                ai_prediction TEXT,
                                report TEXT,
                                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                              )""")

        try:
            self.pg_conn = psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host=os.getenv("POSTGRES_HOST")
            )
            self.pg_cursor = self.pg_conn.cursor()
        except Exception as e:
            print("PostgreSQL not connected:", e)

        self.cache = redis.Redis(host=os.getenv("REDIS_HOST"), port=6379)
        self.ai = AdvancedAIAnalyzer()

    def run_tool(self, tool, args, timeout=30):
        try:
            result = subprocess.run([tool] + args, capture_output=True, text=True, timeout=timeout)
            return result.stdout[:1000]
        except Exception as e:
            return f"{tool} error: {e}"

    @ray.remote
    def audit_logic(self, chain, address, bytecode, usd):
        label, score = self.ai.analyze(bytecode)
        report = ""
        report += self.run_tool("slither", ["Contract.sol"], 20)
        report += self.run_tool("echidna-test", ["Contract.sol"], 30)
        report += self.run_tool("halmos", ["Contract.sol"], 30)
        report += self.run_tool("forge", ["test", "--contracts", "Contract.sol"], 25)
        report += self.run_tool("certora", ["run", "Contract.sol"], 40)
        report += self.run_tool("securify", ["Contract.sol"], 25)

        msg = f"🚨 Contract Audit\nNetwork: {chain}\nAddress: {address}\nBalance: ${usd:.2f}\nAI: {label} ({score:.2f})\nReport:\n{report}"

        requests.post(f"https://api.telegram.org/bot{self.tg_token}/sendMessage", json={"chat_id": self.tg_id, "text": msg})
        if self.discord_webhook:
            requests.post(self.discord_webhook, json={"content": msg})
        if self.slack_webhook:
            requests.post(self.slack_webhook, json={"text": msg})

        self.cursor.execute("INSERT INTO results VALUES (?,?,?,?,?,CURRENT_TIMESTAMP)", (chain, address, usd, label, report))
        self.conn.commit()

        try:
            self.pg_cursor.execute("INSERT INTO results (chain,address,balance,ai_prediction,report) VALUES (%s,%s,%s,%s,%s)",
                                   (chain, address, usd, label, report))
            self.pg_conn.commit()
        except:
            pass

        return True

    async def start_engine(self):
        while True:
            tasks = [self.scan_network(chain, w3) for chain, w3 in self.networks.items()]
            await asyncio.gather(*tasks)
            await asyncio.sleep(5)

    async def scan_network(self, chain, w3):
        try:
            block = w3.eth.get_block("latest", full_transactions=True)
            for tx in block.transactions[:50]:
                if tx.to:
                    code = w3.eth.get_code(tx.to)
                    balance = w3.eth.get_balance(tx.to) / 1e18
                    usd = balance * 3500
                    await self.audit_logic.remote(self, chain, tx.to, code.hex(), usd)
        except Exception as e:
            print(f"Error on {chain}: {e}")

@app.route("/results")
def get_results():
    conn = sqlite3.connect("scanner_results.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM results ORDER BY balance DESC LIMIT 20")
    rows = cursor.fetchall()
    return jsonify(rows)

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("scanner_results.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM results ORDER BY balance DESC LIMIT 20")
    rows = cursor.fetchall()
    html = "<h1>Scanner Results</h1><table border='1'>"
    for row in rows:
        html += "<tr>" + "".join(f"<td>{col}</td>" for col in row) + "</tr>"
    html += "</table>"
    return html

if __name__ == "__main__":
    scanner = OmniReaperProScanner()
    try:
        asyncio.run(scanner.start_engine())
    except KeyboardInterrupt:
        print("Scanner stopped.")
    app.run(host="0.0.0.0", port=5000)
