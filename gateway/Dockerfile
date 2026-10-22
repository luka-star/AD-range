# The range gateway: WireGuard endpoint + router + NAT + firewall, in one container.
# This is the local stand-in for the VPN gateway a real competition runs.
FROM alpine:3.20
RUN apk add --no-cache wireguard-tools iptables iproute2 bash
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
