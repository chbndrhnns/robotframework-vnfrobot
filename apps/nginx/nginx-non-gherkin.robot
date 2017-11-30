*** Settings ***
Library  Network
Library  Runtime
Library  FileSystem

Library  nginx

*** Variables ***
${DESCRIPTOR}   docker-compose.yml

*** Test Cases ***
Available Network Interfaces
    The list of network interfaces on machine is (exactly) ["eth0", "lo"]

    The list of network interfaces on machine contains  "eth0"
    The list of network interfaces on machine contains  "lo"
    The list of network interfaces on machine has size of 2


    The list of network interfaces on machine contains ["eth0", "lo"]
    The list of network interfaces on machine contains one of ["eth0", "lo"]
    The list of network interfaces on machine contains all of ["eth0", "lo"]


    Menge vs. Liste

    Schachtelbarkeit? Komponierbarkeit?
    z.B. Port von innen erreichbar, von außen nicht

    Erweiterbarkeit von innen oder außen
    -> innen (hoisting?)

Network Interface Settings
    Interface 'eth0' has the default gateway '192.168.2.1
    Interface 'eth0' has the property 'MTU size' set to 1400

Open Ports
    [Template] Validate open ports
    80/TCP
    443/TCP

Nginx ports are open
    Given   a container
    When    I check the open ports
    Then


MTU is set correctly
    Given   a container
    When    I look at interface 'eth0'
    Then    the property 'mtu' is set to 1400

    Interface 'eth0' has the property 'mtu'

Website is a mount point
    Given   a descriptor
    Then    there is a volume "/Users/jo/var/www" that is mounted to "/var/www"


Website is mounted
    Given   a container
    When    I enter the directory '/var/www/'
    Then    there is a file 'index.html'
    And     the file 'index.html' contains 'Welcome to NGINX'
    And     the file 'robots.txt' has the attributes {"type": "file", "owner": "www"}


