*** Settings ***
Library  Network
Library  Runtime
Library  FileSystem

Library  nginx

*** Variables ***
${DESCRIPTOR}   docker-compose.yml

*** Test Cases ***
eth0 has a default gateway
    Given   a container
    When    I print the routing table
    Then    interface 'eth0' has a default gateway of '192.168.2.1'

Nginx ports are open
    Given   a container
    When    I check the open ports
    Then


Routing table has all desired entries
    Given   a container
    When    I print the routing table
    Then


MTU is set correctly
    Given   a container
    When    I look at interface 'eth0'
    Then    the property 'mtu' is set to 1400

Website is a mount point
    Given   a descriptor
    Then    there is a volume "/Users/jo/var/www" that is mounted to "/var/www"


Website is mounted
    Given   a container
    When    I enter the directory '/var/www/'
    Then    there is a file 'index.html'
    And     the file 'index.html' contains 'Welcome to NGINX'
    And     the file 'robots.txt' has the attributes {"type": "file", "owner": "www"}


