HTTP Testcase
-------------

*** Settings ***
Documentation
...  This suite contains a basic setup that spawns infrastructure using docker-compose
...  and then performs basics tests
Library     HtmlParser.py
Library     HTTP.py
Library     SuiteTools.py

Suite Setup       Setup test suite  project_path=fixtures/docker-compose
Suite Teardown    Teardown test suite  level=destroy


*** Test Cases ***
Check for correct title in HTML file
    [Documentation]
    ...  HTML files contain titles. Verify that a title is set to a specific value.

    ${response}=    GET http://127.0.0.1/
    Should Be Equal As Strings	${response.status_code}	404

    Parse                       html=${response.text}
#    Assert that title equals "WordPress › Installation"
    Assert that title equals "404 Not Found"
