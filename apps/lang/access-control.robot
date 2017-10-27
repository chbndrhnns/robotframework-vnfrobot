*** Settings ***
Metadata    Version        1.0-pre

Documentation
...  `access-control` describes keywords to write acceptance criteria to VNFs regarding access control
#Address Timeout  500 ms

## TODO: tabular data


*** Keywords ***
User
   [Documentation]
   ...  Validates the status of a linux user.
   ...  objects:
   ...    - user
   ...  arguments:
   ...    - uid: int
   ...    - gid: int
   ...    - groups: []
   ...    - home: str
   ...    - shell: str

   $USER does (not) exist
   $USER  has_attributes=[]

Group
    [Documentation]
    ...  Validate the status of a linux group.
    ...  objects:
    ...    - group
    ...  arguments:
    ...    - gid: int

    [Timeout]
    ... 500 ms

    $GROUP does not exist
    $GROUP does exist
    $GROUP does exist with gid $GID