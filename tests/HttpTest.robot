*** Settings ***
Documentation
...  Test the `HTTP` library which is part of the vnf-robot project.
Library     HTTP
Library     SuiteTools

*** Variables ***

*** Test Cases ***
HTTP GET returns 404 for localhost
    [Documentation]
    ...  Test HTTP GET
    [Setup]  Setup test suite  project_path=tests/fixtures/integration

    ${response}=    GET http://127.0.0.1/
    Should Be Equal As Strings	${response.status_code}	 404

HTTP GET returns error if host is not available
    [Documentation]
    ...  Test HTTP GET and make the test fail if the URL is not reachable.

    Run Keyword and expect error  TimeoutError*  GET http://127.2.0.1:8888/

