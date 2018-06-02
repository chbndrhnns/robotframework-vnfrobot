*** Settings ***
Library   VnfValidator

*** Variables ***
${DESCRIPTOR}     app1-iter-2-refactor.yml

*** Test Cases ***
The deployment has the required services
  [Tags]  [req1]  [req2]
  Set service context to app
  Set service context to redis


