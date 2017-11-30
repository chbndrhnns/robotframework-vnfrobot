*** Settings ***
Documentation
...  Test the `Filesystem` library which is part of the vnf-robot project.
Library     Filesystem
Library     BuiltIn
Library     SuiteTools


*** Test Cases ***
Check for existing file
    [Documentation]
    ...  Test that a file exists on the remote machine
#    [Setup]  Setup test suite  project_path=tests/fixtures/integration

    Run Keyword and expect error  ConnectionError*  127.0.0.1:9980/TCP