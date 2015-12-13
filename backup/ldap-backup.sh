#!/bin/sh
DATE=$(date +%Y%m%d)
edx_ip="172.16.XX.XX"
file_name="ldap_dump-"$DATE".ldif"
/usr/sbin/slapcat >$file_name
#no permission to scp to '/mnt/data_backup/ldap' directly
scp /root/$file_name zyu@$edx_ip:/mnt/data_backup/
