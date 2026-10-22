#!/bin/bash
set -eu

echo "[gateway] enabling IP forwarding"
sysctl -w net.ipv4.ip_forward=1 >/dev/null 2>&1 || true

echo "[gateway] bringing up WireGuard (wg0)"
wg-quick up wg0
for net in 10.60.1.0/24 10.60.2.0/24 10.60.99.0/24; do
    iptables -t nat -A POSTROUTING -d "$net" -j MASQUERADE
done

iptables -A FORWARD -s 10.66.0.0/16 -d "${GS_POSTGRES_IP:-10.60.0.5}" -j DROP

echo "[gateway] ready. Interfaces:"
ip -brief addr show | sed 's/^/[gateway]   /'
echo "[gateway] WireGuard peers:"
wg show || true

while true; do
    sleep 30
    wg show wg0 latest-handshakes 2>/dev/null | sed 's/^/[gateway][wg] /' || true
done
