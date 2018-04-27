*** Settings ***
Library     LowLevel
Variables   common.py


*** Test Cases ***
Check port 6379 is open
    set service context to redis
    Port 6379: state is open

Check port 6379 is listening on localhost
    Port 6379: listening address is 0.0.0.0

Check port 6381 is closed
    Port 6380: state is closed

