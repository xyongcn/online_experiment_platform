open edx在Ubuntu12.04 64上的部署
======

edx_config.backup目录中为OpenEdX服务器上的主要配置文件备份

基本环境信息
======
Ubuntu 12.04.3 LTS (GNU/Linux 3.19.0-25-generic x86_64)

私有: 10.9.19.126, 公有: 172.16.14.147

[Web shell link](https://crl.ptopenlab.com:8800/webshell/aTtlMe0hEB6xzZum/)

[官方安装文档](https://github.com/edx/configuration/wiki/edX-Ubuntu-12.04-64-bit-Installation)

(安装基础环境时请先比对官方提供的包,看是否有更新)

挂载硬盘
======
IBM提供的机器硬盘大小为20G,另附一个130G未格式化的硬盘,openedx需要25G以上空间,所以先进行挂载

(1)分区

    sudo fdisk /dev/vdb
    
按照提示输入m->n(add a new partition)->e(extended)->1(1个分区)

输入柱面号时直接回车使用默认数值即可,完成后输入w保存

如下命令会显示当前分区:

    sudo fdisk -lu
    
(2)格式化并挂载

    sudo mkfs -t ext4 /dev/vdb
    mkdir /devdata
    sudo mount -t ext4 /dev/vdb /devdata
    
(3)配置硬盘在启动时自动挂载

    //记录该命令输出的/dev/vdb对应的uuid
    ls -all /dev/disk/by-uuid
    
    vi /etc/fstab
    //add the following code
    UUID=<UUID>     /devdata     ext4     defaults     0     3

修改umask
======
IBM默认的umask是0077,创建的文件或目录不允许除owner之外的用户读,在安装过程中会出现权限问题

暂时性修改umask,重启后失效

    umask 0002
    
永久修改

    vi /etc/pam.d/common-session
    //uncomment the following code
    session optional pam_umask.so

在以下3个文件中添加 umask 002  

    vi /etc/login.defs
    vi ~/.bashrc
    vi ~/.profile

开始部署edx
======
(1)
更新包

    sudo apt-get update -y
    sudo apt-get upgrade -y
    sudo reboot

(2)
安装所需的软件,pip为包管理系统;使用virtualenv为python开发创建一个隔离的环境

    sudo apt-get install -y build-essential software-properties-common python-software-properties curl git-core libxml2-dev libxslt1-dev libfreetype6-dev python-pip python-apt python-dev libxmlsec1-dev swig
    sudo pip install --upgrade pip
    sudo pip install --upgrade virtualenv

(3)
从github下载配置包

    cd /var/tmp
    git clone -b release https://github.com/edx/configuration
    
为方便ssh访问，
将 configuration/playbooks/roles/common/defaults/main.yml 文件中的变量 COMMON_SSH_PASSWORD_AUTH 更改为 “yes”。

(4)
由于后续的使用ansible的安装过程中elasticsearch可能安装失败，所以在此提前安装elasticsearch

    wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-0.90.3.tar.gz 

    tar xvf elasticsearch-0.90.3.tar.gz   

进入config文件夹，编辑elasticsearch.yml，修改下面两行配置 

    node.name: "name of node"  
    node.master: true

进入到bin目录 

    ./elasticsearch

访问http://host:9200 如果可以访问，说明elasticsearch已经启动。

(5)
利用pip安装包

    cd /var/tmp/configuration
    sudo pip install -r requirements.txt

(6)
利用ansible进行安装,此处耗时可能较长

    cd /var/tmp/configuration/playbooks && sudo ansible-playbook -c local ./edx_sandbox.yml -i "localhost,"
    
提供如下命令选项 

--list-tasks 列出所有安装任务

--start-at-task="where you failed" 从指定位置开始安装,有些任务会依赖于前几个任务,不能直接从该任务开始
    
在安装过程中若gem或pip获取源失败,需要更改至国内源

gem源:

    vi /edx/app/edxapp/edx-platform/Gemfile
    //将源替换成http://ruby.taobao.org
    
pip源(豆瓣的源效果最好,但也不是很稳定,需要多试几次)

    vi <安装目录>/playbooks/roles/common/default/main.yml
    //COMMON_PYPI_MIRROR_URL替换成http://pypi.douban.com/simple
    
elasticsearch获取失败

    vi <安装目录>/playbooks/roles/elasticsearch/default/main.yml
    //将elasticsearch的下载地址从https改为http
    
注意:以上修改完毕后若从头安装,则修改会被覆盖,需要使用--start-at-task 选项进行安装

(7)
安装完成后,在本地的80端口访问lms,18010端口访问studio

(8)
安装XBlock环境

    git clone https://github.com/edx/XBlock.git
    source /edx/app/edxapp/edxapp_env
    cd XBlock
    sudo pip install -r requirements.txt
    
(9)
安装XBlock开发环境(如果你要自己写XBlock的话)
    
    git clone https://github.com/edx/xblock-sdk.git cd xblock-sdk
    mkvirtualenv xblock-sdk
    cd xblock-sdk
    pip install -r requirements.txt
    python manage.py syncdb
    python manage.py runserver 0.0.0.0:8000&
    //浏览器访问本地8000端口即可看到XBlock的相关信息
    //创建新Xblock请使用xblock-sdk中的script/startnew.py脚本
    
(10)
调整时区设置

    vi /edx/app/edxapp/lms.env.json
    vi /edx/app/edxapp/cms/env.json
    将TIME_ZONE参数改为 Asia/Beijing

(11)views.py
用于提供用户初始化接口,与外部系统相连,需要在/edx-platform/lms/urls.py中增加url与views.py函数中的映射
