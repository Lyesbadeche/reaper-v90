FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    openjdk-17-jre-headless \
    pkg-config \
    libssl-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

RUN curl -L https://foundry.paradigm.xyz | bash \
    && /root/.foundry/bin/foundryup
ENV PATH="/root/.foundry/bin:${PATH}"

RUN pip install --no-cache-dir solc-select \
    && solc-select install all \
    && solc-select use 0.8.20

RUN pip install --no-cache-dir slither-analyzer mythril certora-cli halmos

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "main.py"]
