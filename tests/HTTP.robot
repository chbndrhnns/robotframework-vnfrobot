*** Settings ***
Documentation
...  Test the `HTTP` library which is part of the vnf-robot project.
Library     HTTP.py

*** Variables ***
${html}     "<html><head><title>Best title ever</title></head><body></body></html>"


*** Test Cases ***
HTTP GET returns 404 for localhost
    [Documentation]
    ...  Test HTTP GET

    ${response}=    GET http://127.0.0.1/
    Should Be Equal As Strings	${response.status_code}	404
