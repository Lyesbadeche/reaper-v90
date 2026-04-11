FROM ubuntu:22.04

# 1. Environment
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# 2. System dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3-dev \
    openjdk-21-jre-headless \
    curl \
    git \
    build-essential \
    pkg-config \
    libssl-dev \
    libffi-dev \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 3. Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# 4. Foundry
RUN curl -L https://foundry.paradigm.xyz | bash
ENV PATH="/root/.foundry/bin:${PATH}"
RUN /root/.foundry/bin/foundryup

# 5. solc-select
RUN pip3 install --no-cache-dir solc-select \
    && solc-select install 0.8.20 \
    && solc-select install 0.8.19 \
    && solc-select use 0.8.20

# 6. Security tools
# Slither + Mythril are on PyPI
RUN pip3 install --no-cache-dir slither-analyzer mythril

# Certora CLI (download from GitHub releases)
RUN curl -L https://github.com/Certora/cli/releases/latest/download/certora-cli.zip -o certora-cli.zip \
    && unzip certora-cli.zip -d /opt/certora-cli \
    && rm certora-cli.zip
ENV PATH="/opt/certora-cli/bin:${PATH}"

# Halmos (install from GitHub source)
RUN git clone https://github.com/Certora/halmos.git /opt/halmos \
    && cd /opt/halmos \
    && pip3 install .

# 7. Application setup
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 8. Copy project files
COPY . .

# 9. Final execution
EXPOSE 5000
CMD ["python3", "main.py"]


