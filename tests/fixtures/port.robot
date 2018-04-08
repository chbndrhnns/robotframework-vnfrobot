*** Settings ***
Library  LowLevel


*** Variables ***
${DESCRIPTOR}   dc-port.yml


*** Test Cases ***
Check ports
    [Setup]  Set node context to node_1
    Port 12345: state is open

