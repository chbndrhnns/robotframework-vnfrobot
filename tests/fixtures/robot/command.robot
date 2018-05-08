*** Settings ***
Library     VnfValidator
Variables   common.py

*** Variables ***
#${SKIP_UNDEPLOY}    True
#${USE_DEPLOYMENT}   test-2svc

*** Test Cases ***
Version of nginx is 1.13+
    Set service context to sut
    Command "nginx -v": stdout contains "1.13"
