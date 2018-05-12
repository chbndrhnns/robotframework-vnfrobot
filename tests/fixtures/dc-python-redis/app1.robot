*** Settings ***
Library   VnfValidator

*** Variables ***
${DESCRIPTOR}     docker-compose.yml


*** Test Cases ***
Check that the image for the service 'app' contains the correct application code
  [Documentation]  We would like the correct version of the app to be in the Docker image
  ...  (side note: putting the code directly next to the image might be bad)

  Set service context to app
  File 'app.py': contains 'I have been seen'

Check version of Python (2.7+)
  [Documentation]  As Python3 is known not to work with every piece of software, we want to validate that Python2.7
  ...  is in place.

Redis instance is reachable from the app
  [Documentation]  We need to be able to reach Redis via the 'redis' hostname (see the environment variable)

App instance is reachable from redis
  [Documentation]  The app service needs to be reachable from the redis service

Volume for redis is empty after deployment
  [Documentation]  A volume is mounted for redis. It should be empty (contain no files).

REDIS_HOST is set to redis for application
  [Documentation]  The variable is used to make the Python app aware of the redis hostname.

App is listening on port 5000
  [Documentation]  The app exposes port 5000 to the public. We make sure that the port is actually open.

  Set service context to app
  Port 5000: state is open

Redis service is not reachable from a public network
  [Documentation]  Communication between redis and app happens in private, so there is no need to reach redis from the
  ...  public network.

In the network m2m, there are two services
  [Documentation]  Make sure there are only two services at all.

The redis counter increases after sending an HTTP GET to the web server at http://<app>:5000/
  [Documentation]  Validates that the visits to the web site are actually recorded in the redis database.
