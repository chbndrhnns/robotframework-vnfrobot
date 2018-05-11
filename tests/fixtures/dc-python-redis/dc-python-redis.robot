*** Settings ***
Library     VnfValidator

*** Variables ***
${DESCRIPTOR}      ../dc-python-redis/docker-compose.yml
${USE_DEPLOYMENT}  'abc'
${SKIP_UNDEPLOY}    True


*** Test Cases ***
Check ports
  Set service context to app
  Port 5000: state is open
