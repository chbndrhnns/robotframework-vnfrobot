*** Settings ***
Library    ScapyLibrary

*** Test Cases ***
Send And Receive, Return Reply
    Create ICMP Packet
    Send And Get Reply

*** Keywords ***
Create ICMP Packet
    ${ip}     IP      dst=192.168.1.1
    ${icmp}    ICMP
    ${PACKET}    Compose Packet    ${ip}    ${icmp}
    Log Packets    ${PACKET}
    Set Test Variable    ${PACKET}

Send And Get Reply
    ${reply}    Send And Receive At Layer3    ${PACKET}    timeout=${10}
    Log Packets    ${reply[0]}
    ${reply}       Send And Receive At Layer3    ${PACKET}    timeout=${10}    return_send=${True}
    Log Packets    ${reply[0][0]}
    Log Packets    ${reply[0][1]}
    ${reply}    ${unanswered}    Send And Receive At Layer3    ${PACKET}    timeout=${10}    return_send=${True}    return_unanswer=${True}
    Log Packets    ${reply[0][0]}
    Log Packets    ${reply[0][1]}
    Should Be Equal As Integers    ${unanswered.__len__()}    0