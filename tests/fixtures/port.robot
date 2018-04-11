*** Settings ***
Library     LowLevel
Variables   common.py


*** Test Cases ***
Check ports
    Set service context to sut
    Port 12345: state is closed

