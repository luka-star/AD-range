#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

OUT=wireguard
mkdir -p "$OUT"

GW_WAN_IP=10.80.0.254           
LAPTOP_ENDPOINT="${1:-127.0.0.1}"

echo "[gen-wg] generating keys ..."
gen_keys() {
  if command -v wg >/dev/null 2>&1; then
    for n in gw p1 p2 laptop; do
      priv=$(wg genkey); pub=$(printf '%s' "$priv" | wg pubkey); echo "$n $priv $pub"
    done
  else
    docker run --rm alpine:3.20 sh -c '
      apk add --no-cache wireguard-tools >/dev/null 2>&1
      for n in gw p1 p2 laptop; do
        priv=$(wg genkey); pub=$(printf "%s" "$priv" | wg pubkey); echo "$n $priv $pub"
      done'
  fi
}

while read -r name priv pub; do
  case "$name" in
    gw) gw_priv=$priv; gw_pub=$pub ;;
    p1) p1_priv=$priv; p1_pub=$pub ;;
    p2) p2_priv=$priv; p2_pub=$pub ;;
    laptop) lp_priv=$priv; lp_pub=$pub ;;
  esac
done < <(gen_keys)

echo "[gen-wg] writing $OUT/wg0.conf (gateway)"
cat > "$OUT/wg0.conf" <<EOF
# Gateway (server) config. Address range 10.66.0.0/16 is the VPN/player space.
[Interface]
Address = 10.66.0.1/16
ListenPort = 51820
PrivateKey = $gw_priv

[Peer]
# team1 player
PublicKey = $p1_pub
AllowedIPs = 10.66.1.100/32

[Peer]
# team2 player
PublicKey = $p2_pub
AllowedIPs = 10.66.2.100/32

[Peer]
# your macOS laptop (optional; net number 3)
PublicKey = $lp_pub
AllowedIPs = 10.66.3.100/32
EOF

write_player() {   # $1=file $2=address $3=privkey
  cat > "$OUT/$1" <<EOF
[Interface]
Address = $2/32
PrivateKey = $3

[Peer]
PublicKey = $gw_pub
Endpoint = $GW_WAN_IP:51820
# Route the whole range (vulnboxes 10.60.0.0/16 + other players 10.66.0.0/16) through the tunnel.
AllowedIPs = 10.60.0.0/16, 10.66.0.0/16
PersistentKeepalive = 25
EOF
}

echo "[gen-wg] writing $OUT/player1.conf, $OUT/player2.conf"
write_player player1.conf 10.66.1.100 "$p1_priv"
write_player player2.conf 10.66.2.100 "$p2_priv"

echo "[gen-wg] writing $OUT/laptop.conf (import into the macOS WireGuard app, optional)"
cat > "$OUT/laptop.conf" <<EOF
[Interface]
Address = 10.66.3.100/32
PrivateKey = $lp_priv

[Peer]
PublicKey = $gw_pub
# If connecting from another machine, change this to your Mac's LAN IP.
Endpoint = $LAPTOP_ENDPOINT:51820
AllowedIPs = 10.60.0.0/16
PersistentKeepalive = 25
EOF

chmod 600 "$OUT"/*.conf
echo "[gen-wg] done. Configs in ./$OUT/"
