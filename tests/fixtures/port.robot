*** Settings ***
Library  LowLevel

*** Variables ***
#${SKIP_DEPLOY}  True
${SKIP_UNDEPLOY}  True
${DESCRIPTOR}   dc-test.yml

*** Test Cases ***
Check ports
    Set service context to sut
    Port 12345: state is open

