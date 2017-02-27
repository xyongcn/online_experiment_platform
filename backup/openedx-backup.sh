#!/bin/sh
DATE=$(date +%Y%m%d)
file_name="/root/tmp_mongo_backup/mongo_dump-"$DATE
mongo_user="secret"
mongo_pwd="secret"
mongodump -u $mongo_user -p $mongo_pwd -o $file_name
mv $file_name /mnt/data_backup/openedx/
mv /mnt/data_backup/*.ldif /mnt/data_backup/ldap/
