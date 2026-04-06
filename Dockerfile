# Stage 1: Builder
FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3.10 python3-pip python3-dev \
    curl git build-essential libssl-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN curl -L https://foundry.paradigm.xyz | bash && /root/.foundry/bin/foundryup

RUN pip3 install --no-cache-dir solc-select slither-analyzer halmos certora-cli
RUN solc-select install 0.8.20 && solc-select use 0.8.20

RUN pip3 install --no-cache-dir mythril

# Stage 2: Runner
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apt-get update && apt-get install -y \
    python3.10 python3-pip openjdk-21-jre-headless curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.10/dist-packages /usr/local/lib/python3.10/dist-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /root/.foundry /root/.foundry

ENV PATH="/root/.foundry/bin:${PATH}"

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python3", "main.py"]
