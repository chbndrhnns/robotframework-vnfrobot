*** Keywords ***
# Execution Context
Get Environment Variables
    [Documentation]     Retrieve environment variables that are set for a container.
    ...                 Tags: runtime, execution_context
    [Return]    ${vars}

Execute Command
    [Documentation]     Run a command and return exit code, stdout and stderror.
    ...                 Tags: runtime, execution_context
    [Arguments] ${command}
    [Return]    ${code}   ${stdout} ${stderr}

Get Process
    [Documentation]     Retrieve information about a process: pid, state,
    ...                 Tags: runtime, execution_context
    [Arguments] ${process}
    [Return]    ${pid}    ${state}

Get Service
    [Documentation]     Retrieve information about a process: pid, state,
    ...                 Tags: runtime, execution_context
    [Arguments] ${service}
    [Return]   ${state}

Get Kernel Parameters
    [Return]    ${parameters}

# Meta Data
Inspect Container
    [Arguments] ${container}
    [Return]    ${inspection}

# Access Control
Check User
    [Arguments]     ${user}
    [Return]        ${user}

Check Group
    [Arguments]     ${group}
    [Return]        ${group}

# File
Check File
    [Arguments]     ${file}
    [Return]        ${file}

Check Symlink
    [Arguments]     ${symlink}    ${destination}
    [Return]        ${is_symlink}

# Connectivity
Check Address
    [Arguments]     ${address}
    [Return]        ${result}

Resolve DNS Record
    [Arguments]     ${record_type}    ${record}
    [Return]        ${result}

Get Interface
    [Arguments]     ${interface}
    [Return]        ${result}

Check Port
    [Arguments]     ${port}   ${protocol}
    [Return]        ${result}


