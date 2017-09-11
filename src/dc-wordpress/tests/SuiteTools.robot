*** Settings ***
Documentation
...  Test the `SuiteTools` library which is part of the vnf-robot project.
Library     BuiltIn
Library     SuiteTools.py


*** Test Cases ***
Create Docker containers from a docker-compose.yml file
    [Documentation]     A docker-compose.yml file is used to create a test setup
    [Setup]             Setup test suite  project_path=fixtures/integration

    No Operation

    [Teardown]          Teardown test suite  level=destroy

