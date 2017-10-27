*** Settings ***
Metadata    Version        1.0-pre

Documentation
...  `filesystem` describes keywords to write acceptance criteria to VNFs regarding the file system

## TODO: tabular data


*** Keywords ***
File
    [Documentation]
    ...  Validate the status of a file record.
    ...  objects:
    ...    - file
    ...    - symbolic link
    ...    - directory
    ...  attributes:
    ...    - size: int
    ...    - mode: int
    ...    - owner:
    ...    - group:
    ...    - type: Enum(file, link, dir)
    ...    - contains: []
    ...    - checksum: Enum(md5, sha256)
    ...    - link: str

    [Timeout]
    ... 500 ms

    $OBJECT  exists

    $OBJECT  has_attributes=[{'size':$SIZE}]


Mount point
    [Documentation]
    ...  Validates the status of a mount point.
    ...  objects:
    ...    - mount point
    ...  arguments:
    ...    - options: []
    ...    - fs-type: str
    ...    - destination: str

    $MOUNT_POINT does exist
    $MOUNT_POINT  has_attributes=[arguments]



