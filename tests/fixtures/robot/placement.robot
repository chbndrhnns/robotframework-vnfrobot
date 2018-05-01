*** Settings ***
Library     VnfValidator
Variables   common.py


*** Test Cases ***
Service "sut" is on docker swarm master
    set service context to redis
    Placement: node.role is manager

