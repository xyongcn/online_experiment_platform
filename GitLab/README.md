参照[官网](https://about.gitlab.com/downloads/)的安装步骤

注:IBM提供的外部url的映射要求内部地址必须有一级目录,即website/os_gitlab的形式

git_config.backup目录中为Gitlab服务器上的配置文件备份

[API使用说明](https://github.com/gitlabhq/gitlabhq/tree/master/doc/api)

安装完成后,做如下修改:

[user.rb备份](https://github.com/rainymoon911/online_experiment_platform/blob/master/GitLab/git_config.backup/users.rb)

1.设置gitlab在/os_gitlab子目录中访问

以下为官方提供的需要修改的配置:(/opt/gitlab/embedded/service/gitlab-rails/config)

    1) In your application.rb file: config.relative_url_root = "/os_gitlab"
    2) In your gitlab.yml file: relative_url_root: /os_gitlab
    3) In your unicorn.rb: ENV['RAILS_RELATIVE_URL_ROOT'] = "/os_gitlab"
    4) In ../gitlab-shell/config.yml: gitlab_url: "http://127.0.0.1/os_gitlab"
    5) In lib/support/nginx/gitlab: do not use asset gzipping,remove block starting with "location = ^/(assets)/"
    
在新版的gitlab中,以上配置文件中除了１,5之外都无法直接修改,每次reconfigure之后会被覆盖,官方也没有再gitlab.rb中提供相关配置

需要直接修改模板,模板目录为 /opt/gitlab/embedded/cookbooks/gitlab/templates/default/

找到模板目录中对应的配置文件的模板,修改完毕后运行

    cd /opt/gitlab/embedded/service/gitlab-rails/
    export PATH=/opt/gitlab/embedded/bin:$PATH
    sudo -u git -H env PATH=$PATH && bundle exec rake assets:precompile RAILS_ENV=production
    sudo gitlab-ctl reconfigure



2.去除邮件激活


    vi ./embedded/service/gitlab-rails/lib/api/users.rb
    
在create user函数中加入如下语句
    
    user.skip_confirmation!
    if user.save
    ...

[gitlab.rb备份](https://github.com/rainymoon911/online_experiment_platform/blob/master/GitLab/git_config.backup/gitlab.rb)

3.去除前台的注册功能(默认是关闭的,若开启,按下列步骤关闭)

    vi /etc/gitlab/gitlab.rb
    gitlab_rails['gitlab_signup_enabled'] = false
    //使配置生效
    sudo gitlab-ctl reconfigure

4.配置不允许用户修改邮件:

    vi /etc/gitlab/gitlab.rb
    gitlab_rails['gitlab_username_changing_enabled'] = false
    //使配置生效
    sudo gitlab-ctl reconfigure
    
5.去除邮件查重(由于shibboleth登录时会报邮件已存在的错误,不像OpenEdX能与本地账号绑定)

6.创建教师账号,用户名teacher,教师以管理员的账号在Docker的配置文件中会用到
