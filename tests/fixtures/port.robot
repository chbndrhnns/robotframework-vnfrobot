*** Settings ***
Library  LowLevel

*** Variables ***
#${USE_DEPLOYMENT}
${SKIP_UNDEPLOY}  True
${DESCRIPTOR}   dc-test.yml

*** Test Cases ***
Check ports
    Set service context to sut
    Port 12345: state is open

