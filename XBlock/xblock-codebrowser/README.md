代码编辑器XBlock
======

###1.首先安装Woboq codebrowser及其所需的环境

[官方配置文档](https://github.com/woboq/woboq_codebrowser/)

[Woboq配置及使用](https://github.com/xyongcn/code-viewer/blob/master/document_by_zyu/woboq%E5%AE%89%E8%A3%85%E4%B8%8E%E4%BD%BF%E7%94%A8.md)

###2.创建代码以及浏览页面的存放目录

    sudo -u www-data bash
    cd <path of xblock-codebrowser>
    ./scripts/create_dir.sh
    cp -r your_woboq_codebrowser_file/* /edx/var/edxapp/woboq_codebrowser/
    cp ./scripts/generator.sh /edx/var/edxapp/staticfiles/xblock-script/
    cp ./scripts/make.sh /edx/var/edxapp/staticfiles/xblock-script/

注意:必须确保www-data用户拥有scripts中脚本的执行权限以及所创建目录的读写权限,脚本第一次运行时会连接Gitlab服务器,系统会询问是否添加fingerprint,所以要事先以edxapp用户连接一次Gitlab以添加fingerprint

    sudo -u edxapp bash
    ssh user@gitlab_ip
    //select yes to add fingerprint

###3.替换学生界面的code-editor XBlock的URL

* 在部署完code-editor之后记录下该学生页面该XBlock对应的URL,并做如下操作:

    vi <path_of_xblock-codebrowser>/codebrowser/static/js/src/codebrowser_view.js>

* 将如下语句中的URL替换成code-editor对应的URL,

    window.location.href = "http://166.111.68.45:11133/courses/BIT/CS101/2014T1/courseware/0b64b532c9f44b2c9c23a87a2b1f8104/da4d2d1648bf49baa59c08715acfcd38/";
    
###4.安装XBlock

填写config.py配置文件中的Gitlab的ip以及端口
    
    sudo -u edxapp /edx/bin/pip.edxapp install <path_of_xblock-codebrowser>

卸载命令:

    sudo -u edxapp /edx/bin/pip.edxapp uninstall xblock-codebrowser
    

    

    
    
    



