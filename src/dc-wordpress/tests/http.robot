HTTP Testcase
-------------

*** Settings ***
Library     /Users/jo/dev/master/vnf-robot/src/dc-wordpress/tests/HtmlParser.py
Library     /Users/jo/dev/master/vnf-robot/src/dc-wordpress/tests/HTTP.py

Suite Setup       Setup test suite
Suite Teardown    Teardown Actions


*** Test Cases ***
Check for correct title in HTML file
    [Documentation]  HTML files contain titles. Verify that a title is set to a specific value.

    ${response}=    GET http://127.0.0.1/
    Should Be Equal As Strings	${response.status_code}	200

    Parse                       html=${response.text}
    Assert that title equals "WordPress › Installation"
