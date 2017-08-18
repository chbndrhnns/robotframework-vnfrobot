HTTP Testcase
-------------

*** Settings ***
Library     /Users/jo/dev/master/vnf-robot/src/dc-wordpress/tests/HtmlParser.py
Library	    RequestsLibrary

*** Test Cases ***
Check for correct title in HTML file
      Parse     html="<html><head><title>Test title</title><body>Test body</body></html>"
      Verify title equals "Test title"

#Get Requests
#    Create Session  wordpress	http://127.0.0.1
#
#    ${resp}=	Get Request	wordpress   /
#    Should Be Equal As Strings	${resp.status_code}	200
#
#    ${root} =	Parse XML	${resp.text}
#    ${elem} =	Get Element	${root}	//title
#    Should Be Equal  ${elem}  'WordPress &rsaquo; Installation'



