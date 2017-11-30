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

