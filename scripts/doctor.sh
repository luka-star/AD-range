#!/usr/bin/env bash
# Quick connectivity check across every layer of the range. Run after `make core` (and `make players`).
set -u
cd "$(dirname "$0")/.."
C="docker compose"
ok()   { printf "  \033[32m[ ok ]\033[0m %s\n" "$1"; }
bad()  { printf "  \033[31m[FAIL]\033[0m %s\n" "$1"; }
note() { printf "  \033[33m[note]\033[0m %s\n" "$1"; }

echo "== Gameserver =="
curl -sf -o /dev/null http://localhost:8000/competition/scoreboard && ok "web scoreboard reachable (http://localhost:8000)" || bad "web not reachable on :8000"
if curl -sf http://localhost:8000/competition/teams.json | grep -q '"teams"'; then ok "teams.json served (controller + web alive)"; else bad "teams.json missing"; fi
nc -z -w2 localhost 6666 2>/dev/null && ok "submission TCP :6666 reachable" || bad "submission not reachable on :6666"

echo "== Checker -> vulnbox (through the gateway/NAT) =="
for t in 1 2 99; do
  if $C exec -T checker1 curl -sf -o /dev/null "http://10.60.$t.2:10067/health"; then ok "checker1 can reach vulnbox 10.60.$t.2:10067"; else bad "checker1 cannot reach 10.60.$t.2:10067 (vulnbox down or routing)"; fi
done

echo "== Gateway / WireGuard =="
$C exec -T gateway wg show wg0 >/dev/null 2>&1 && ok "gateway wg0 is up" || bad "gateway wg0 not up"

echo "== Players (only if started with 'make players') =="
if $C ps --services --filter status=running 2>/dev/null | grep -q '^player1$'; then
  $C exec -T player1 ping -c1 -W2 10.60.2.2 >/dev/null 2>&1 && ok "player1 reaches team2 vulnbox over VPN (10.60.2.2)" || bad "player1 cannot reach 10.60.2.2 over VPN"
  if $C exec -T player1 sh -c 'nc -z -w2 10.60.0.5 5432' 2>/dev/null; then bad "player1 CAN reach the gameserver DB (should be blocked!)"; else ok "player1 correctly blocked from the gameserver DB"; fi
else
  note "players not running; start them with 'make players'"
fi
echo "done."
