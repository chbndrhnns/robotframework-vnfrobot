*** Settings ***
Metadata    Version        1.0-pre
Metadata    More Info      For more information about *easy-voting-app* see https://github.com/dockersamples/example-voting-app
Metadata    Executed At    ${HOST}

Documentation
...  ```easy-voting-app``` is a sample project that can be deployed on a Docker swarm environment.
...  This file contains acceptance tests for the `Worker` component.

Library     HtmlParser
Library     Socket
Library     HTTP

*** Test Cases ***
Docker build
    [Documentation]
    ... Verifies that the `docker build` command works for the `worker` container.

    [Tags] runtime
    Given a test environment
    When I build the container image for worker
    Then no error occurs

Worker process
    [Documentation]
    ...  The worker container is set up properly.

    src/Worker/Worker.dll  has_attributes=[{'type': 'file'}]

Connectivity
    [Documentation]
    ...  The worker needs to be able to connect to the postgresql proccess and to the redis database.

    [Tags] network

    # TODO: can the
    Define FUN(service, port):

    Given a test environment
    When I try to connect to ${service} on ${port}
    Then it succeeds


    | *Test Case* | *service*              | *port*     |
    | 1 | db      | db                     | 5432/tcp   |
    | 2 | redis   | redis                  | 6379/tcp   |


Postgresql login (GWT)
    [Documentation]
    ...  The worker instance can login to the postgresql db.

    Given a deployment
    When I connect to the db instance
    Then I can login with user "postgres"


Postgresql login (single data set)
    [Documentation]
    ...  The worker instance can login to the postgresql db.

    postgresql login is possible  user=postgres  password=None


Postgresql login (table)
    [Documentation]
    ...  The worker instance can login to the postgresql db.

    Given a deployment
    When I connect to the db instance
    Then I can login with ${user} and ${password}

    | *Test Case*    | *username*       | *password*     |
    | 1 | login      | user             | None           |


Redis (table style)
    [Documentation]
    ...  The worker instance can use the Redis database.

    Given a deployment of redis
    When I connect to it
    Then I can store {'foo': 'bar'}
    And I can retrieve 'foo'

DNS lookup
    [Documentation]
    ...  The


