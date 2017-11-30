*** Settings ***
Metadata    Version        1.0-pre
Metadata    More Info      For more information about *easy-voting-app* see https://github.com/dockersamples/example-voting-app
Metadata    Executed At    ${HOST}

Documentation
...  ```easy-voting-app``` is a sample project that can be deployed on a Docker swarm environment.
...  This file contains acceptance tests for the `voting-app` component.

Library     HtmlParser
Library     Socket
Library     HTTP

*** Test Cases ***
Layer 4 Connectivity
    Given a deployment
    When I try to connect to ${service} on ${port}
    Then it succeeds

    | *Test Case* | *service*              | *port*     | *network*   |
    | 1 | redis   | redis                  | 6379/tcp   | back-tier   |
    | 2 | vote    | vote                   | 5001/tcp   | front-tier  |
    | 3 | result  | result                 | 5002/tcp   | front-tier  |

API implementation according to the specification
    Given a deployment
    When I verify the API endpoints
    Then I see no errors
    Then I see all succeed
    Then all succeed
    Then I see no errors


Log listener
    Given a deployment
    And a login

Redirect HTTP requests to HTTPS
