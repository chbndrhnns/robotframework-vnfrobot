*** Keywords ***
# Execution Context
Get Environment Variables
    [Return]    $vars

Execute Command
    [Arguments] $command
    [Return]    $code   $stdout $stderr

Get Process
    [Arguments] $process
    [Return]    $state

Get Service
    [Arguments] $service
    [Return]   $state

Get Kernel Parameters
    [Return]    $parameters

# Meta Data
Inspect Container
    [Arguments] $container
    [Return]    $inspection

# Access Control
Get User
    [Arguments]     $user
    [Return]        $user

Get Group
    [Arguments]     $group
    [Return]        $group

# File
Get File
    [Arguments]     $file
    [Return]        $file

Get Symlink
    [Arguments]     $symlink    $destination
    [Return]        $is_symlink

# Connectivity
Check Address
    [Arguments]     $address
    [Return]        $result

Resolve DNS Record
    [Arguments]     $record_type    $record
    [Return]        $result

Get Interface
    [Arguments]     $interface
    [Return]        $result

Check Port
    [Arguments]     $port   $protocol
    [Return]        $result

# Application: HTTP
Send HTTP Request
    [Arguments]     $type   $headers    $body
    [Return]        $code   $headers    $body

