*** Keywords ***
OPENAPI_FILE  "openapi.yaml"

REST API at ${url} conforms to the specification at

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

    ${URL}= http://ui.demo.local/login

    GET $URL returns $STATUS
    GET $URL returns one of [$STATUS]
    GET $URL contains [$BODY]

    Kernel Parameter    "net.ip4.forwarding"        is           1
    Kernel Parameter    "net.ip4.forwarding"        is not       1
    Kernel Parameter    "net.ip4.forwarding"        contains     1
    Kernel Parameter    "net.ip4.forwarding"        contains not 1


    Kernel Parameter    "vm.user_reserve_kbytes"    is greater  58000
    Kernel Parameter    "vm.user_reserve_kbytes"    is greater  58000

*** Keywords ***
