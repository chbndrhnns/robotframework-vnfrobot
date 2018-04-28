*** Settings ***
Library     VnfValidator
Variables   common.py

*** Variables ***
${DESCRIPTOR}   dc-test.yml


*** Test Cases ***
Check ports
  Set service context to sut
  Port 8080/tcp: state is open
