

ENV DEBIAN_FRONTEND=noninteractive ENV TZ=UTC

RUN apt-get update && apt-get install -y 
python3.10 python3-pip python3-dev 
openjdk-21-jre-headless 
curl git build-essential pkg-config 
libssl-dev libffi-dev wget unzip 
&& rm -rf /var/lib/apt/lists/*

RUN curl –proto ‘=https’ –tlsv1.2 -sSf https://sh.rustup.rs | sh -s – -y ENV PATH=”/root/.cargo/bin:${PATH}”

RUN curl -L https://foundry.paradigm.xyz | bash ENV PATH=”/root/.foundry/bin:${PATH}” RUN /root/.foundry/bin/foundryup

RUN pip3 install –no-cache-dir solc-select 
&& solc-select install 0.8.20 
&& solc-select install 0.8.19 
&& solc-select use 0.8.20

RUN pip3 install –no-cache-dir slither-analyzer mythril certora-cli halmos

WORKDIR /app COPY requirements.txt . RUN pip3 install –no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000 CMD [“python3
