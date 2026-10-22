#!/bin/bash
# Connect this player into the range over WireGuard, then idle so you can `exec` exploits in it.
set -eu

echo "[player] bringing up WireGuard (wg0)"
wg-quick up wg0

# Best-effort: install the exploit bundle's own dependencies if they are mounted.
if [ -f /exploits/requirements.txt ]; then
    echo "[player] installing /exploits/requirements.txt"
    pip install --no-cache-dir -r /exploits/requirements.txt || \
        echo "[player] WARNING: could not install exploit requirements (offline?); requests+pycryptodome are already present"
fi

echo "[player] connected. wg status:"
wg show || true
echo "[player] ready. Run exploits with:  docker compose exec $(hostname) python3 /exploits/<exploit>.py <vulnbox-ip> <flag-id>"
exec tail -f /dev/null
