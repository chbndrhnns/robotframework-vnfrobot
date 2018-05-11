*** Settings ***
Library   VnfValidator

*** Variables ***
${DESCRIPTOR}     docker-compose.yml
${USE_DEPLOYMENT}  'fervent_wescoff'


*** Test Cases ***
Check that the image for the service 'app' contains the correct application code
  [Documentation]
  
  Set service context to app
  File 'app.py': contains 'I have been seen'

Check version of Python (2.7+)
  [Documentation]
  
Redis instance is reachable from the app
  [Documentation]
  
App instance is reachable from redis
  [Documentation]
  
Volume for redis is empty after deployment
  [Documentation]
  
REDIS_HOST is set to redis for application
  [Documentation]
  
App is listening on port 5000
  [Documentation]
  Set service context to app
  Port 5000: state is open

Redis service is not reachable from a public network
  [Documentation]
  
In the network m2m, there are two services
  [Documentation]
  
The redis counter increases after sending an HTTP GET to the web server at http://<app>:5000/
  [Documentation]
  