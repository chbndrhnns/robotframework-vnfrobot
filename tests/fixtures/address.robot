*** Settings ***
Library     LowLevel
Variables   common.py

*** Test Cases ***
Check if google.com is reachable
    Set network context to sut
    Address www.google.com: is reachable

Check that another address is not reachable
    Address "www.googlebla.com": is not reachable
