*** Settings ***
Documentation
...  Test the `Socket` library which is part of the vnf-robot project.
Library     Socket


*** Test Cases ***
check open ports
    [Documentation]
    ...  Test that ports are accessible on localhost
#    [Setup]  Setup test suite  project_path=tests/fixtures/integration

    127.0.0.1:9980/TCP
    127.0.0.1:9981/TCP
    127.0.0.1:9982/TCP
    127.2.0.1:9983/TCP
    127.0.0.1:9984/TCP
    127.0.0.1:9985/TCP
    google.de:443/TCP

check open ports again
    [Documentation]
    ...  Test again that ports are accessible on localhost
#    [Setup]  Setup test suite  project_path=tests/fixtures/integration

    127.0.0.1:9980/TCP
    127.0.0.1:9981/TCP
    127.0.0.1:9982/TCP
    fdvnionsdv.de:9983/TCP
    127.0.0.1:9984/TCP
    127.0.0.1:9985/HFNDBD
    127.0.0.1:9986/TCP

