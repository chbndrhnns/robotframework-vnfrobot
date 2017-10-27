*** Settings ***
Metadata    Version        1.0-pre

Documentation
...  `network` describes keywords to write acceptance criteria to VNFs regarding network connectivity

#Address Timeout  500 ms

## TODO: tabular data


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

    I can (not) reach $ADDRESS
    $ADDRESS is (not) reachable
    Connection to $ADDRESS is (not) possible

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

    Use DNS server $DNS_SERVER

    $NAME is (not) resolved to $ADDRESS
    $NAME is (not) resolved to [$ADDRESS]
    $NAME is only resolved to $ADDRESS

    $NAME resolves to $ADDRESS
    $NAME resolves to [$ADDRESS]
    $NAME only resolves to $ADDRESS

    Lookup of $NAME1 is (not) successful

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

   $INT is configured with []
   $INT is (not) enabled

   $INT is not configured


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

    Process is (not) listening on [$ADDRESS:]$PORT/$PROTOCOL
    (Not) listening on $PORT/$PROTOCOL

    $ADDRESS:$PORT/$PROTOCOL is open
    $ADDRESS:$PORT/$PROTOCOL is closed


HTTP GET
    [Documentation]
    ...  Validate an HTTP GET response.
    ...  objects:
    ...    - url
    ...  arguments:
    ...    - status: Enum(HTTP Response)
    ...    - body: [str]

    [Timeout]
    ... 1000 ms

    [Settings]
    ... follow-redirects: true

    GET $URL returns $STATUS
    GET $URL returns one of [$STATUS]
    GET $URL contains [$BODY]




