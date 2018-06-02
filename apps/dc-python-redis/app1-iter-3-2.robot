*** Settings ***
Library   VnfValidator

*** Variables ***
${DESCRIPTOR}     app1-iter-3-2.yml

*** Test Cases ***
The deployment has the required services
  [Tags]  [req1]  [req2]
  Set service context to app
  Set service context to redis

The "app" service contains the correct application files.
  [Tags]  [req3]
  Set service context to app
  File 'app.py': contains 'I have been seen'

