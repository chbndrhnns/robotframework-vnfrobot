*** Settings ***
Library     LowLevel
Variables   common.py


*** Test Cases ***
Check port 6379
    set service context to redis
    Port 6379: state is open

