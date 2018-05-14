*** Settings ***
Library     VnfValidator
Variables   common.py

*** Test Cases ***
Check that another address is not reachable
    Set service context to sut