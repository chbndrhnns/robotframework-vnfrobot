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

   ${USER} does (not) exist
   ${USER}  has_attributes=[]

   User ${USER} does exist
   User ${USER} does not exist
   Users [${USER}, ${USER} do exist
   Users [${USER}, ${USER} do not exist
   User ${USER} does exist with properties {"uid": "123", "groups": "www"}
   User ${USER} has the properties {"uid": "123", "groups": "www"}

Group
    [Documentation]
    ...  Validate the status of a linux group.
    ...  objects:
    ...    - group
    ...  arguments:
    ...    - gid: int

    [Timeout]
    ... 500 ms

    Group ${GROUP} does exist
    Group ${GROUP} does not exist

    Groups [${GROUP1}, ${GROUP2} do exist
    Groups [${USER}, ${USER} do not exist

    Group ${USER} does exist with properties {"uid": "123", "groups": "www"}