部署顺序:uc_docker->xblock-codeeditor->xblock-codebrowser
====

[部署文件备份,供参考](https://github.com/rainymoon911/online_experiment_platform/tree/master/OpenEdX/edx_config.backup)

###配置XBlock所使用的mongodb

*openedx自带mongodb,无需再安装,输入mongo命令即可进入数据库命令行,若出现"Failed global initialization: BadValue Invalid or no user locale set",执行如下命令

        export LC_ALL=C
        
*建立XBlock所用的数据库

        mongo
        use test
        db.createCollection(token)//用于XBlock间共享用户私钥以获取在Gitlab上的代码
        db.createCollection(codeview)//用于存储用户正在浏览,编辑的文件
        db.createCollection(cluster)//用于存储docker信息
        db.createCollection(ldap)//用于存储用户的ldap信息
        
*为test数据库设置访问验证,默认任何人都能访问数据库

        vi /etc/mongod.conf 
        set auth=true

重启mongo 
        sudo stop mongod
        sudo start mongod

配置管理员信息

        mongo
        use admin
        db.addUser('username','secret')
        
退出并重新进入mongo命令行

        mongo
        use admin
        db.auth('username','secret')
        use test
        db.addUser('username','secret')

###使xblock可用

* edx-platform/lms/envs/common.py中去掉注释：

        #from xmodule.x_module import prefer_xmodules
  
        #XBLOCK_SELECT_FUNCTION = prefer_xmodules
  
* edx-platform/cms/envs/common.py,中去掉注释：

        #from xmodule.x_module import prefer_xmodules
        #XBLOCK_SELECT_FUNCTION = prefer_xmodules
    
* edx-platform/cms/envs/common.py中把

        'ALLOW_ALL_ADVANCED_COMPONENTS'以及 'ADVANCED_SECURITY'设置为True
    

###XBlock安装完成后需重启服务:

    sudo /edx/bin/supervisorctl -c /edx/etc/supervisord.conf restart edxapp:
    sudo /edx/bin/supervisorctl -c /edx/etc/supervisord.conf restart edxapp_worker:
    
###在后台高级设置中advanced_modules添加XBlock
