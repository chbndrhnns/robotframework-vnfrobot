*** Settings ***
Library     VnfValidator

*** Variables ***
${SKIP_UNDEPLOY}    True
${USE_DEPLOYMENT}   ha

*** Test Cases ***
#Check node version
#    Set service context to awesome
#    Command "node --version": stdout contains v10
#
#Check npm view command
#    Set service context to awesome
#    Command "npm view": stderr contains "Invalid"
#
#Npm can reach the repository server
#    Set service context to awesome
#    command "npm ping": stdout contains "success"

m2m network can reach the internet
    Set network context to web
    Address www.google.com: is reachable