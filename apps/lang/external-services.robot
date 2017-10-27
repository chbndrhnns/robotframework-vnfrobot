*** Keywords ***

Test Response
    Given a successful deployment of ${stack}
    When ${request} is sent to ${host}
    Then ${response} is the expected reponse.


Lifecycle Operation
    Given a successful deployment of ${stack}

    When ${node} transitions from ${state} to ${state}
    Then


    When scaling ${node} to ${count} instances
    Then

    When killing ${count} instances of ${node}
    Then

    When killing ${node}
    Then

    When listing all services
    Then [${service}] are running

    Then


Performance
    Given a successful deployment of ${stack}

    When I send ${count}


Replay Traffic
    Given a successful deployment of ${stack}
    When I replay ${file} on ${node} with ${options}
    Then I expect


Application server
    Given a successful deployment of ${stack}
    And a ${application_type} server for running on ${protocol://address:port} with options {}
    And it is set up to reply with ${responses}

    When ${node} connects to it
    When ${node} queries it with ${request}

    Then no errors occurs