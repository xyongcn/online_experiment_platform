#!/bin/sh
DATE=$(date +%Y%m%d)
file_name="/mnt/date_backup/openedx/mongo_dump-"-$DATE
mongo_pwd="secret"
mongodump -u edxapp -p $mongo_pwd -o $file_name
mv /mnt/data_backup/*.ldif /mnt/data_backup/ldap/
