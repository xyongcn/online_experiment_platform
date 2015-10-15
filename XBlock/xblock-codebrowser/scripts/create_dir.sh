#!/bin/bash

#sudo -u www-data bash
cd /edx/var/edxapp
# where your woboq_codebrowser should put
mkdir woboq_codebrowser && chown www-data:www-data woboq_codebrowser

#the dir you put static html files that user browse
cd staticfiles
mkdir codebrowser && chown www-data:www-data codebrowser

#the dir you put code
mkdir ucore && chown www-data:www-data ucore

#the dir you put scripts
mkdir xblock-script && chown www-data:www-data xblock-script


#the git config file which used to switch users of gitlab and use the proper private key
cd /var/www
mkdir .ssh && cd .ssh
touch config
chmod 600 config
cd ../ && chown -R www-data:www-data .ssh
