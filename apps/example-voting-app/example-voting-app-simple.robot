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
    192.168.99.100:80/tcp
    192.168.99.100:5858/tcp


HTML sites are served
#    [Tags] layer7
    [Documentation]
    ...  Test <title> tag

    ${response}=    GET http://192.168.99.100:5000
    Parse           html=${response.text}
    Assert that title equals "Cats vs Dogs!"

#Get services
#
#Get instances count
#
#Get log files
#
#Get inventory
#
#Get logs (continuosly?)

#