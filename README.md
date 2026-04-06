# 🛡️ OmniReaperPro: Advanced Smart Contract Security Scanner

## 🚀 Overview
An enterprise-grade security scanner combining **AI (Transformers)** with **Formal Verification tools** (Slither, Echidna, Certora) to detect vulnerabilities in real-time.

## 🛠️ Tech Stack
- **AI Engine:** DistilBERT for bytecode classification.
- **Scanners:** Slither, Mythril, Halmos, Forge.
- **Backend:** Python (Asyncio), Ray (Parallel processing).
- **Database:** PostgreSQL & Redis.

## 📦 How to Run
1. Clone the repo.
2. Setup environment variables (RPCs, Telegram Token).
3. Run using Docker:
   ```bash
   docker-compose up --build

