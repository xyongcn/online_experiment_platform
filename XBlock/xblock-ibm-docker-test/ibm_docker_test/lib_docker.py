__author__ = 'zyu'

import paramiko
from lib_util import Util

class DockerHelper(object):

    logger = Util.ibm_logger()

    def __init__(self, git_host, init_user,init_pwd):
        self._git_host = git_host
        self._init_user = init_user
	self._init_pwd = init_pwd

    #create user for student
    def init_user(self,host,user_name,user_pwd):
	self.logger.info("init_user " + host + " " + user_name + " " + user_pwd)
	cmd =  "./myuseradd-ibm " + user_name + " " + user_pwd
        print cmd
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=self._init_user, password=self._init_pwd)
        stdin,stdout,stderr=ssh.exec_command(cmd)
        print stdout.read()
        ssh.close()

    #initialize git config
    def init_git(self,host,user_name,user_pwd,email,git_name,private_key,public_key):
	self.logger.info("init docker git" + " " + email + " " + user_name)
	cmd = "umask 0002 ; mkdir .ssh ; "
        cmd += "echo -ne '" + private_key + "' >~/.ssh/id_rsa ; "
        cmd += "echo '" + public_key + "' >~/.ssh/id_rsa.pub ; "
        cmd += "chmod 0600 ~/.ssh/id_rsa ; "
        cmd += "eval 'ssh-agent -s' ; "
        cmd += "ssh-add ~/.ssh/id_rsa ; "
        cmd += "git config --global user.name '" + user_name + "' ; "
        cmd += "git config --global user.email " + email + " ; "
        #cmd += "sudo echo -ne 'StrictHostKeyChecking no\\nUserKnownHostsFile /dev/null\\n' >> /etc/ssh/ssh_config && "
        cmd += "mkdir ucore_lab ; cd ./ucore_lab && git init ; "
        #cmd += "git remote add origin_edx " + repo_url +"; " 
        cmd += "git remote add origin_edx git@" + self._git_host + ":" + git_name + "/ucore_lab.git ; "
        cmd += "git pull origin_edx master"
	self.logger.info("cmd" + cmd)
        print cmd
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=user_name, password=user_pwd)
        stdin,stdout,stderr=ssh.exec_command(cmd)
        print stdout.read()
        ssh.close()

