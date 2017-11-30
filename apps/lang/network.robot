*** Settings ***
Metadata    Version        1.0-pre

Documentation
...  `network` describes keywords to write acceptance criteria to VNFs regarding network connectivity

#Address Timeout  500 ms

*** Keywords ***
Network Address
    [Documentation]
    ...  Validate if an address is reachable from within a container.
    ...  objects:
    ...    - IPv4 address
    ...    - IPv6 address
    ...    - domain name
    [Timeout]
    ... 500 ms

    ${NODE}=postgresql
    ${ADDRESS}=8.8.8.8

    From ${NODE}, I can (not) reach $ADDRESS
    ${ADDRESS} is (not) reachable
    Connection to ${ADDRESS} is (not) possible

DNS lookup
    [Documentation]
    ...  Validate if a DNS lookup is successful.
    ...  Supported DNS records are:
    ...  - `A` IPv4 address
    ...  - `AAAA` IPv6 address
    ...  - `CNAME` domain alias
    ...  - `NS` name server
    ...  - `PTR` pointers for reverse DNS lookups
    ...  - `SRV` propagate IP-based services
    ...  - `TXT` free-text records

    [Timeout]
    ... 500 ms

    ${DNS}=8.8.8.8
    ${NAME}=bla.blub.com

    Use DNS server ${DNS_SERVER}

    ${NAME} is (not) resolved to ${ADDRESS}
    ${NAME} is (not) resolved to [${ADDRESS}]
    ${NAME} is only resolved to ${ADDRESS}

    ${NAME} resolves to ${ADDRESS}
    ${NAME} resolves to [${ADDRESS}]
    ${NAME} only resolves to ${ADDRESS}

    Lookup of ${NAME} is (not) successful

    '<name> [<ttl>] IN <type> <rdata>' is (not) resolved


Network Interface
   [Documentation]
   ...  Validate the status of a network interface.
   ...  object:
   ...    - interface: str
   ...  arguments:
   ...    - addresses: []
   ...    - mtu: []
   ...    - active: Boolean
   ...    - mac-address: str

   ${INT}=eth0

   MTU 1500 is configured on ${INT}
   Mac address AA:BB:CC:DD:EE:FF is configured on ${INT}
   10.0.0.2/22 is configured on ${INT}
   10.0.0.2/22 is configured on ${INT}

   Interface ${INT} has the address fe80::76:8dc3:ffe6:4e09
   Interface ${INT} has the addresses [fe80::76:8dc3:ffe6:4e09, 127.0.0.1/32]


Network Port
    [Documentation]
    ...  Validates the status of a port.
    ...  objects:
    ...    - port: int
    ...    - protocol: Enum(UDP,TCP)
    ...  arguments:
    ...    - address

    [Timeout]
    ...  500 ms

    ${PORT}=22245

    On node ${NODE}, port ${PORT} is open.
    On node ${NODE}, port ${PORT} is closed.

    From node ${NODE1}, port ${PORT} is open on ${NODE2}
    From node ${NODE1}, port ${PORT} is closed on ${NODE2}


    ${ADDRESS}:${PORT}/${PROTOCOL} is open on node postgresql.
    ${ADDRESS}:${PORT}/${PROTOCOL} is closed on node postgresql.





