该XBlock用于为用户分配IBM所提供的docker资源,并定时或由用户手动回收

1.修改hosts,否则api无法访问url

    vi /etc/hosts
    #add the following code
    172.16.10.120 crl.ptopenlab.com
    
2.XBlock安装的python-ldap需要依赖包如下

    sudo apt-get install python-dev libldap2-dev libsasl2-dev libssl-dev
    
3.XBlock安装/卸载

    cd <dir of xblock>
    sudo -u edxapp /edx/bin/pip.edxapp install .
    sudo -u edxapp /edx/bin/pip.edxapp uninstall ibm_docker-xblock-test
    
