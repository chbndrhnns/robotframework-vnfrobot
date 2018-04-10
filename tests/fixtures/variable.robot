*** Settings ***
Library  LowLevel

*** Variables ***
#${SKIP_DEPLOY}      True
${SKIP_UNDEPLOY}    True
#${DEPLOYMENT_NAME}
${DESCRIPTOR}       dc-test.yml

*** Test Cases ***
Check variables
    Set service context to sut
    Variable PATH: contains "usr"
    Variable PATH: contains not Python
    Variable NGINX_VERSION: is 1.13.11-1~stretch
