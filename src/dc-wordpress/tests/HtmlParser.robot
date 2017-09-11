*** Settings ***
Documentation
...  Test the `HtmlParser` library which is part of the vnf-robot project.
Library     HtmlParser.py

*** Variables ***
${html}     "<html><head><title>Best title ever</title></head><body></body></html>"


*** Test Cases ***
<title> equals
    [Documentation]
    ...  Test <title> tag

    Parse           html=${html}
    Assert that title equals "Best title ever"
