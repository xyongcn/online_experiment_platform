数据备份:

Openedx与Gitlab上均映射了nfs:/mnt/data_backup

挂载nfs：

sudo apt-get install nfs-common
sudo mount -t nfs softrepo.ptopenlab.com:/gpfs/user/tsinghua/ /mnt/data_backup

导出mongo数据库

    mongodump -h IP -p 端口 -u 用户名 -p 密码 -d 数据库 -o 文件存在路径
    (eg. mongodump -u 用户名 -p 密码 -o mongo_dump-20121124)
    
若在本地可省略-h,-p
省略-d 则导出所有数据库

导入全部数据库:

    Mongorestore <path of dump file>

Gitlab仓库目录:([Gitlab管理说明文档](https://gitlab.com/gitlab-org/omnibus-gitlab/blob/master/README.md))

/var/opt/gitlab/git-data.
该目录下包含gitlab-satellites(仓库代码)以及repositories(.git配置以及相关信息)

导出所有信息:（[官方备份说明文档](http://doc.gitlab.com/ce/raketasks/backup_restore.html#create-a-backup-of-the-gitlab-system)）

    sudo gitlab-rake gitlab:backup:create
    
nfs目录git无写权限,需先导出,后由root mv至nfs目录。由于导出的压缩文件在10G左右,将默认的导出目录设置为/git-data.temp,该目录挂载了120G的硬盘,用于暂时存放,执行上述命令后在/git-data.temp可看到压缩的数据文件。

数据导入:

    # Stop processes that are connected to the database
    sudo gitlab-ctl stop unicorn
    sudo gitlab-ctl stop sidekiq

    #This command will overwrite the contents of your GitLab database!
    sudo gitlab-rake gitlab:backup:restore BACKUP=1393513186
    # Start GitLab
    sudo gitlab-ctl start
    # Check GitLab
    sudo gitlab-rake gitlab:check SANITIZE=true

导出

    /usr/sbin/slapcat > <file name.ldif>
    
导入

    slapadd -l <file name.ldif>
