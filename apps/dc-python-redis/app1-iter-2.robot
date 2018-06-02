*** Settings ***
Library   VnfValidator

*** Variables ***
${DESCRIPTOR}     app1-iter-2.yml

*** Test Cases ***
[req1] The deployment has a service "app"
  Set service context to app

[req2] The deployment has a service "redis"
  Set service context to redis