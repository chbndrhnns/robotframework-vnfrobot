*** Settings ***
Library     VnfValidator

*** Variables ***
${DESCRIPTOR}      ../dc-python-redis/docker-compose.yml
#${USE_DEPLOYMENT}  'abc'
#${SKIP_UNDEPLOY}    True


*** Test Cases ***
Check that the image for the service 'app' contains the correct application code
    Set service context to app
    File 'app.py': contains 'I have been seen'

Check version of Python (2.7+)

Redis instance is reachable from the app

App instance is reachable from redis

Volume for redis is empty after deployment

REDIS_HOST is set to redis for application

App is listening on port 5000
  Set service context to app
  Port 5000: state is open

Redis service is not reachable from a public network

In the network m2m, there are two services

The redis counter increases after sending an HTTP GET to the web server at http://<app>:5000/
