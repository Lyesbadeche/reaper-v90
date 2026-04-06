FROM ubuntu:22.04

# 1. Fix environment variables (Split to avoid "missing =" error)
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# 2. Install all system dependencies
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

# 3. Install Rust and set PATH
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# 4. Install Foundry and set PATH
RUN curl -L https://foundry.paradigm.xyz | bash
ENV PATH="/root/.foundry/bin:${PATH}"
RUN /root/.foundry/bin/foundryup

# 5. Install solc-select and configure versions
RUN pip3 install --no-cache-dir solc-select \
    && solc-select install 0.8.20 \
    && solc-select install 0.8.19 \
    && solc-select use 0.8.20

# 6. Install all security analysis tools (Slither, Mythril, Certora, Halmos)
RUN pip3 install --no-cache-dir slither-analyzer mythril certora-cli halmos

# 7. Setup Application
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 8. Copy project files
COPY . .

# 9. Final execution
EXPOSE 5000
CMD ["python3", "main.py"]
