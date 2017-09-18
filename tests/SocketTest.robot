*** Settings ***
Documentation
...  Test the `Socket` library which is part of the vnf-robot project.
Library     Socket
Library     BuiltIn
Library     SuiteTools


*** Test Cases ***
check open ports
    [Documentation]
    ...  Test that ports are accessible on localhost
#    [Setup]  Setup test suite  project_path=tests/fixtures/integration

    Run Keyword and expect error  ConnectionError*  127.0.0.1:9980/TCP
    Run Keyword and expect error  ConnectionError*  127.0.0.1:9981/TCP
    Run Keyword and expect error  ConnectionError*  127.0.0.1:9982/TCP
    Run Keyword and expect error  TimeoutError*     127.2.0.1:9983/TCP
    Run Keyword and expect error  ConnectionError*  127.0.0.1:9984/TCP
    Run Keyword and expect error  ConnectionError*  127.0.0.1:9985/TCP
    google.de:443/TCP

check open ports again
    [Documentation]
    ...  Test again that ports are accessible on localhost
    # [Setup]  Setup test suite  project_path=tests/fixtures/integration

    Run Keyword and expect error  ConnectionError*   127.0.0.1:9980/TCP
    Run Keyword and expect error  ConnectionError*   127.0.0.1:9981/TCP
    Run Keyword and expect error  ConnectionError*   127.0.0.1:9982/TCP
    Run Keyword and expect error  *Error*   fdvnionsdv.de:9983/TCP
    Run Keyword and expect error  ConnectionError*   127.0.0.1:9984/TCP
    Run Keyword and expect error  DataFormatError*   127.0.0.1:9985/HFNDBD
    Run Keyword and expect error  ConnectionError*   127.0.0.1:9986/TCP

