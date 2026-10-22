# A "team player": a machine that connects into the range over WireGuard and runs exploits.
# Stands in for a competitor's laptop.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        wireguard-tools iproute2 iptables curl ca-certificates netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*
# Common exploit libraries (the GIFaway exploits use requests; pycryptodome covers crypto tasks).
RUN pip install --no-cache-dir requests pycryptodome
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
