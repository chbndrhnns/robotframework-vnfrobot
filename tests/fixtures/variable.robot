*** Settings ***
Library  LowLevel

*** Variables ***
${USE_DEPLOYMENT}   frosty_einstein
${SKIP_UNDEPLOY}    True
${DESCRIPTOR}       dc-test.yml

*** Test Cases ***
Check variables
    Set service context to sut
    Variable PATH: contains "usr"
    Variable PATH: contains not Python
    Variable NGINX_VERSION: is 1.13.11-1~stretch
