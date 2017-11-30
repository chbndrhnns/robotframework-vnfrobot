*** Settings ***
Metadata    Version        1.0-pre

Documentation
...  `runtime` describes keywords to write acceptance criteria to VNFs regarding the runtime environment

## TODO: tabular data


*** Keywords ***
Environment Variable
    [Documentation]
    ...  Validate the presence and content of environment variables.
    ...  objects:
    ...    - variable
    ...  arguments:
    ...    - content: str

    ...  use: https://stackoverflow.com/a/39993106/6112272
    [Setup]  set context

    $ENV is (not) set
    $ENV is (not) set to $CONTENT

    $ENV contains $CONTENT
    $ENV does not contains $CONTENT


Command
    [Documentation]
    ...  Validate the exit status of a command.
    ...  objects:
    ...    - command
    ...  arguments
    ...     - exit-status: int
    ...     - stream: Enum(stdout, stderr)
    ...     - output: str

    [Timeout]
    ... 1000 ms

    $COMMAND exits with $EXIT_STATUS
    $COMMAND exits with $EXIT_STATUS and $STREAM contains $OUTPUT
    $COMMAND exits with $EXIT_STATUS and $STREAM contains $OUTPUT

Process
    [Documentation]
    ...  Validates the running status of a process.
    ...  objects:
    ...    - process name

    Process $PROCESS is (not) running

Service
    [Documentation]
    ...  Validates the status of a linux service.
    ...  Supported frameworks: upstart, systemd, init
    ...  objects:
    ...    - service name
    ...  arguments:
    ...    - enabled
    ...    - running

    Service $SERVICE is (not) running
    Service $SERVICE is (not) enabled


Package
    [Documentation]
    ...  Validate the status of a package.
    ...  (Support for yum and apt)
    ...  objects:
    ...    - package
    ...  arguments:
    ...    - version

    $PACKAGE [$VERSION] is (not) installed


Kernel parameters
    [Documentation]
    ...  Validates the status of a kernel parameter.
    ...  objects:
    ...    - parameter
    ...  arguments:
    ...    - value: str

    Kernel parameter $PARAMETER is set to $VALUE
    Kernel parameter $PARAMETER is not set to $VALUE
    Kernel parameter $PARAMETER contains $VALUE


Placement constraint
    [Documentation]
    ...  Validates the usage of a placement constraint.
    ...  objects:
    ...    - constraint

    Container is (not) on host $(HOST)
    Container is (not) on node $(NODE_ID)
    Container is (not) on node with role $(ROLE)
    Container is (not) on node with labels []