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

    ${TYPE} = 'file' or 'symbolic link' or 'directory'

    ${TYPE} ${OBJECT} does exist
    ${TYPE} ${OBJECT} does not exists


    ${TYPE} ${OBJECT} has the property  size  123 GB
    ${TYPE} ${OBJECT} has the property  mode  777
    ${TYPE} ${OBJECT} has the property  mode  u+r
    ${TYPE} ${OBJECT} is a link
    ${TYPE} ${OBJECT} contains 'text'
    ${TYPE} ${OBJECT} is of type 'text'
    ${TYPE} ${OBJECT} has not the property  size  123 GB



    ${TYPE} ${OBJECT} has the properties {""}]]

    File '/var/log/apache.log' links to '/var/log/bla'
    File '/var/log/apache.log' contains 'string'
    File '/var/log/apache.log' checksum is ''
    File '/var/log/apache.log' belongs to group 'www'
    File '/var/log/apache.log' belongs to user 'root'

    Size of file '/var/log/apache.log/ is  <operator>
    Mode of file '/var/log/apache.log' is 0755
    Owner of file '/var/log/apache.log' is 0755
    Group of file '/var/log/apache.log' is 'admin'
    'APACHE WEBSERVER' is in file '/var/log/apache.log'
    SHA256 checksum of file '' is 55ab01ec393d082048357fb688635354aba82d2400e2a4d79a68c7eea1323efa
    'var/system/settings.conf' is a file
    'var/system/settings' is a directory
    'var/system/settings.conf' is a link


Mount point
    [Documentation]
    ...  Validates the status of a mount point.
    ...  objects:
    ...    - mount point
    ...  arguments:
    ...    - options: []
    ...    - fs-type: str
    ...    - destination: str

    Mount point ${$MOUNT_POINT} does exist
    Mount point ${$MOUNT_POINT} does not exist

    Mount point ${MOUNT_POINT} has the destination ""
    Mount point ${MOUNT_POINT} points to ${destination}

