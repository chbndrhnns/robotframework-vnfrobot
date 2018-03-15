*** Keywords ***

# Application: HTTP
Send HTTP Request
    [Arguments]     ${type}   ${headers}    ${body}
    [Return]        ${code}   ${headers}    ${body}

