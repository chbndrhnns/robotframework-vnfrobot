*** Settings ***
Library   VnfValidator

*** Variables ***
#${USE_DEPLOYMENT}   ha

*** Test Cases ***
Reducing amount of replicas of awesome and see if requrests are still answered
  [Documentation]  The proxy directs incoming requests to the discovered web servers.
  ...  After changing the amount of available web server, all requests should still be answered.

Web server should not be reachable from the `public` network
  [Documentation]  Any request to a web server should only be possible via the load balancer.
  [Tags]  network_context

  Set network context to public
  Address "awesome:8080": is not reachable

Web server serves a web site
  [Documentation]  Validate that there is a 200 OK reply when sending a request.

proxy discovers two services
  [Documentation]  HAProxy should have discovered as many services as replicas are specified for the service "awesome"
  ...  Should be two during the test.

HAProxy load balancing mode is set to least_connected
  [Documentation]  HAProxy supports different ways of load balancing
  ...  (https://poweruphosting.com/blog/haproxy-load-balancing-algorithms/)

PATH variable set correctly on service "aweseome"
  [Documentation]  We required /usr/sbin to be in the system PATH

  Set service context to awesome
  Variable PATH: contains "/usr/sbin"

Web server ignores HTTP POST requests
  [Documentation]  The web server should throw away any other requests than GET

Average response time of web server is below 5 ms
  [Documentation]  All responses for a number of requests should be within the specified limit
  ...  The parametrization for this test should be:
  ...  - send 500 requests with 50 being in flight at the same time

Load balancer has access to the Docker socket
  [Documentation]  For service discovery, HAProxy access the host Docker socket to retrieve information about the
  ...  labels of other containers. Whenever a SERVICE_PORT label occurs, this container is added to the instances used
  ...  for load balancing.
  [Tags]  placement_context

  Set service context to proxy
  Placement: node.role is manager

Check node version
  [Documentation]  Node.js is available in so many different version that incompatibilities are hard to avoid.
  ...  We check that we have at least version v9.X.X

  Set service context to awesome
  Command "node --version": stdout contains v9

Check npm view command
  [Documentation]  Running the `view` command should fail as there is no `package.json` file

  Set service context to awesome
  Command "npm view": stderr contains "Invalid"

Npm can reach the repository server
  [Documentation]  Ensure that the package manager can reach the repository.

  Set service context to awesome
  command "npm ping": stdout contains "success"

m2m network can reach the internet
  [Documentation]  From the m2m network, we would like access to the internet.

  Set network context to web
  Address www.google.com: is reachable