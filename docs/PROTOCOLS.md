# Protocol and transport matrix

A protocol is not the same thing as a transport or TLS mode.

| Combination | Provisioning | Default | Requirements |
|---|---|---|---|
| VLESS / WebSocket / TLS | automatic | on | TLS edge + WS |
| Trojan / WebSocket / TLS | automatic | on | TLS edge + WS |
| VMess / WebSocket / TLS | automatic | on | TLS edge + WS |
| VLESS / HTTPUpgrade / TLS | automatic alpha preset | off | compatible edge + client |
| VLESS / XHTTP / TLS (packet-up) | automatic alpha preset | off | compatible HTTP edge + client; no guarantee across proxies |
| VLESS / REALITY / Vision | explicit template helper | off | direct TCP and generated keys, explicit authorized target; configure Vision on users |
| Shadowsocks | upstream editor | off | matching cipher, credentials and exposed ports |
| Hysteria2 | upstream editor/node | off | supported node/core, UDP/QUIC, TLS certificate |
| WireGuard | upstream separate node | off | UDP, interface/routing and OS privileges |

No TLS verification bypass is enabled. No public unauthenticated SOCKS/HTTP proxy is created. Private IP destinations are blocked in automatic Xray profiles. The ordinary Docker/VPS bundle only exposes web edge traffic; advanced TCP/UDP node port mappings must be configured separately.

Presets are selected only during initialization with `SABI_PROFILES`. Every user must use one of the generated templates or explicitly select the `sabi-ray-all` group. Users intentionally left without a group are NOT silently granted access by a background watcher.

Default empty client lists are expected; the panel manages user identifiers on the node. Do not hand-edit credentials in source files.
