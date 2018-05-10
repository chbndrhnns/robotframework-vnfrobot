*** Settings ***
Library     VnfValidator
Variables   common.py

*** Variables ***
${REDIS_BINARY}     /usr/local/bin/redis-server


*** Test Cases ***
redis binary is executable
    set service context to redis
    File ${REDIS_BINARY}: state is existing
    File ${REDIS_BINARY}: mode is executable

hosts file contains
    File /etc/hosts: contains

