*** Settings ***
Library   VnfValidator

*** Variables ***
${DESCRIPTOR}     app1-iter-1.yml

*** Test Cases ***
[req1] The deployment has a service "app"
  Set service context to app

