*** Settings ***
Metadata    Version        1.0-pre
Metadata    More Info      For more information about *easy-voting-app* see https://github.com/dockersamples/example-voting-app
Metadata    Executed At    ${HOST}

Documentation
...  ```easy-voting-app``` is a sample project that can be deployed on a Docker swarm environment.
...  This file contains acceptance tests for the project.

Library     HtmlParser
Library     Socket
Library     HTTP

*** Test Cases ***
Sockets can be reached
#    [Tags] layer4
    [Documentation]
    ...  Check if the required sockets are open on the deployed nodes

    192.168.99.100:5000/tcp
    192.168.99.100:8080/tcp
    192.168.99.100:5001/tcp


HTML site main
#    [Tags] layer7
    [Documentation]
    ...  Test if correct HTML content is served for main page

    ${response}=    GET http://192.168.99.100:5000
    Parse           html=${response.text}
    Assert that title equals "Cats vs Dogs!"


HTML site of result
#    [Tags] layer7
    [Documentation]
    ...  Test if correct HTML content is served for main page

    ${response}=    GET http://192.168.99.100:5001
    Parse           html=${response.text}
    Assert that title equals "Cats vs Dogs -- Result"

HTML site of status
#    [Tags] layer7
    [Documentation]
    ...  Test if correct HTML content is served for main page

    ${response}=    GET http://192.168.99.100:8080
    Parse           html=${response.text}
    Assert that title equals "Visualizer"