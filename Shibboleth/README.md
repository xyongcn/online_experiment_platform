# MOOC 平台
以下配置文件涉及的内容有：gitlab的安装，Open edX的安装，利用Shibboleth实现以gitlab和Open edX作为两个SP实现SSO（单点登录）。
<hr/>

**目录**
* [框架图](#framework)
* [gitlab的安装](#gitlab)
* [Open edX的安装](#openEdx)
* [shibboleth](#Shibboleth)
 + [部署LDAP服务器](#LDAP)
 + [部署IdP](#IdP)
 + [布署Open edX端的SP](#SP-edx)
 + [布署Gitlabu端的SP](#SP-gitlab)

<hr/>

<h1 id="framework">框架图</h1>
![framework](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/Shibboleth-framework.png)

单点登录的过程如下：（以Gitlab为例）

+ **1.用户访问资源（Gitlab）**

用户尝试访问受保护的资源（Gitlab）。资源监视器决定用户是否有活跃的会话，发现用户没有（没有登录过），把用户指向服务提供者（IdP）

+ **2.服务提供者（SP）发表认证请求**

用户到达服务提供者（SP），服务提供者准备一个认证请求并发送请求和用户给身证提供者（IdP）。

+ **3.用户在身份提供者（IdP）处被认证**

当用户到达身份提供者（IdP），IdP检查用户是否有一个存在的会话。如果有，前进到下一步。如果没有，IdP认证它们（例如：提示并检查一个用户名和密码）然后用户前进到下一步。

+ **4.身份提供者（IdP）发表认证响应**

在认证了用户之后，身份提供者准备一个认证响应并把响应和用户发送回服务提供者（SP）。

+ **5.服务提供者（SP）检查认证响应，资源返回内容**

当用户带者来自身份提供者的响应到达时，服务提供者将会确认响应，为用户创建一个会话，使从响应中检索到的一些信息（例如：用户的标识符）可用来保护资源。
用户现在再次尝试访问受保护的资源，但是这一次用户己经有一个会话并且资源知道用户是谁。有了这些信息，资源将会服务用户的请求并且发送用户请求的数据

<hr/>
<h1 id="gitlab"> 1.gitlab的安装</h1>
## 1.1环境

    gitlab版本：GitLab CE Omnibus 
    
    操作系统：ubuntu 12.04 64bit
    
## 1.2安装gitlab

   下面的安装步骤参考的是[官方文档](https://about.gitlab.com/downloads/#ubuntu1204)
    
### (1). 安装前查看端口状态，并把80和8080端口解除占用

   由于gitlab安装结束后会占用80和8080端口，所以如果你的操作系统中己有apache,tomcat那么这两个端口是处于占用状态的，会导致安装gitlab后访问localhost时出现502错误。因此，我们先释放这两个端口。
   
输入下面的命令查看端口状态：
```
     sudo netstat -anptl
```
如下图所示：

![netstat -anptl](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/gitlab-install-0.png)

然后找到80,和8080端口对应的pid
输入：
```
kill -9 <pid>  
```
例如上图中，这里只有8080端口被占用，80没有被占用，我只需解除8080的占用即可(8080端口对应的PID为1213)。输入“kill -9 1213”

-----下面内容可选做-------

因为在gitlab这里用不到tomcat，而tomcat默认端口为8080,与gitlab的unicorn端口(8080)冲突，所以为了不必要的麻烦，可以直接把tomcat的默认端口改掉。通过下的的操作实现把tomcat的端口改为8088:
```
vi /etc/tomcat7/server.xml

```
找到8080端口，如下
```
 <Connector port="8080" protocol="HTTP/1.1"
               connectionTimeout="20000"
               URIEncoding="UTF-8"
               redirectPort="8443" />
```
把它改为8088，如下：
```
 <Connector port="8088" protocol="HTTP/1.1"
               connectionTimeout="20000"
               URIEncoding="UTF-8"
               redirectPort="8443" />
```
保存更改。
输入下面的命令重启tomcat：
```
sudo service tomcat7 restart
```

----------end--------------
### (2)安装和配置必要的依赖

输入下面的命令：
```
sudo apt-get install curl openssh-server ca-certificates postfix
```
在安装过程中选择“Internet Site”。

 出现下面的内容说明安装成功：
 
![netstat -anptl](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/gitlab-install-1.png)

### (3)添加gitlab 包服务并安装包
输入下面的命令:
```
curl -sS https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash
```
出现下面的内容仓库说明己安装好：

![netstat -anptl](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/gitlab-install-2.png)

然后输入下面的命令安装包：
 ```
 sudo apt-get install gitlab-ce
 ```
 
 出现下面的内容说明安装好：
 
 ![netstat -anptl](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/gitlab-install-3.png)
 
 
### (4)配置并重启Gitlab

输入下面的命令：
```
sudo gitlab-ctl reconfigure
```

出现下面的内容说明配置成功：

![netstat -anptl](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/gitlab-install-4.png)

### (5)登录gitlab(访问http://localhost)
  在浏览器中输入：http://localhost 如果进入到登录页面，则说明gitlab己正确安装。
  首次访问gitlab,会直接重定向到设置密码屏幕，初始用户名是root。
  
<h1 id="openEdx"> 2.Open edX的安装</h1>
## 2.1 环境

Open edX版本：Open edX Fullstack

操作系统：Ubuntu12.04 64bit

## 2.2 服务器要求

+ Ubuntu 12.04 amd64
+ 最小4GB内存
+ 至少一个2GHz CPU 或 EC2 计算单元
+ 最小25GB可用硬盘，生产服务器需要最小50GB可用硬盘

## 2.3 安装Open edX

以下安装步骤参考的是[此文档](https://openedx.atlassian.net/wiki/display/OpenOPS/Native+Open+edX+Ubuntu+12.04+64+bit+Installation#title-heading)，采用的是自动安装的方法进行安装。

### (1) 更新源和升级软件

依次输入下面的三条命令：
```
sudo apt-get update -y  
sudo apt-get upgrade -y  
sudo reboot  
```
### (2)安装Open edX

依次输入下面的两条命令：
```
wget https://raw.githubusercontent.com/edx/configuration/master/util/install/ansible-bootstrap.sh -O - | sudo bash
wget https://raw.githubusercontent.com/edx/configuration/master/util/install/sandbox.sh -O - | bash
```
**注意!** 一般来说第一条命令可以正常执行。第二条命令就开始安装了，耗时比较长，如果顺利的话2个小时左右，但一般都不会一次成功…………出现错误了（会以红色标示），安装会中止，这时候就需要根据出错的提示解决掉错误，然后重新执行第二条命令，如此反复，直到没有错误（failed=0）,就安装成功了！

安装成功后访问：http://localhost 可进行学生端LMS访问，出现登录页面。

访问：http://localhost:18010 可进行Studio访问

---------------------
下面是我在安装过程中出现的错误，及解决方法：

#### 错误1：
[insights | run r.js optimizer]*******************************************************************

找不到jquery.js脚本。错误提示如下：
![netstat -anptl](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-install-0.png)

#### 解决方法：
(1)下载jquery.js 。下载地址：https://jquery.com/  ,把下载的jquery-3.1.1.js(任何一个版本都可以) 重命名为jquery.js

(2)把下载好的jquery.js文件放到/edx/app/insights/edx_analytics_dashboard/analytics_dashboard/static/bower_components/jquery/dist/目录下

(3) 重新执行
```
wget https://raw.githubusercontent.com/edx/configuration/master/util/install/sandbox.sh -O - | bash
```

#### 错误2：
[insights | run collectstatics]******************************************************************************

stderr:CommandError:Anerror occurred during rendering .....

错误截图如下：

![netstat -anptl](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-install-1.png)

#### 解决方法：
使用java-7-openjdk 设置环境变量，通过以下步骤实现：

(1)输入下面的命令：
```
sudo update-alternatives --config java  
```
选择java-7-openjdk

如下图所示：
![netstat -anptl](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-install-2.png)

(2)设置环境变量：

输入下面的命令：
```
JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64/jre/bin/java  
```

把上面的/usr/lib/jvm/java-7-openjdk-amd64/jre/bin/java 换成你实际选择的java路径

(3)重新执行命令
```
wget https://raw.githubusercontent.com/edx/configuration/master/util/install/sandbox.sh -O - | bash
```
----------------------------
如果出现红色（fail）,但是又ignoring，则可以不用管，还是会安装成功的。如出现[mysql | Look for mysql 5.6]失败，后面它ignoring了，也不会影响安装成功。
![netstat -anptl](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-install-3.png)


---
  
<h1 id="Shibboleth"> 3.Shibboleth</h1>


<h2 id="LDAP"> 3.1 部署LDAP服务器.</h2>


### 3.1.1 安装OpenLDAP及可视化工具

[我们所使用的OpenLDAP镜像](http://www.turnkeylinux.org/openldap)

该镜像已包含phpldapadmin(方便网页端访问LDAP),若从其他渠道安装LDAP,请自行安装该工具。

### 3.1.2 利用eduperson.ldif创建模式eduPerson

    ldapadd -Y EXTERNAL -H ldapi:/// -f <path of eduperson.ldif>
    
### 3.1.3 登录管理员账号创建存储用户的结点,例如ou=Users,dc=cscw

或者使用命令行添加Users节点:

	ldapadd -x -D "cn=admin,dc=cscw" -W -f create_group.ldif
 
把上面代码中的"cn=admin,dc=cscw" 换成你登录ldapadmin时的LoginDN。LoginDN的位置如下图所示

### 3.1.4 test_ldap.py可用于测试OpenLDAP是否正常工作(修改其中的ip,baseDN以及searchFilter参数,保持与IDP中的配置一致,
详细可参考shibboleth仓库中的配置文件)

### 3.1.5 create_user.ldif用于手动创建用户(修改其中的用户参数)

    ldapadd -x -D "cn=admin,dc=cscw" -W -f create_user.ldif 
    
把上面代码中的"cn=admin,dc=cscw" 换成你登录ldapadmin时的LoginDN。

![netstat -anptl](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/openLdap-0.png)

create_user.ldif的内容如下：
```
dn: uid=Tom,ou=Users,dc=cscw
objectClass: inetOrgPerson
objectClass: top
objectClass: eduPerson
uid: Tom
sn: Tom
givenName:Tom
cn:Tom
mail:yannizhang8800@163.com
userPassword: 123456
eduPersonPrincipalName:yannizhang8800@163.com
```

+ 把代码中所有的Tom换成你要新建的用户名;

+ yannizhang8800@163.com 换成该用户名对应的邮箱，注意邮箱应是唯一的，因为Open edX是以邮箱为主键的。

+ 123456 换成该用户的密码

+ 第一行中的 ou=Users,dc=cscw换成你的实际路径。

如下图，我们创建的新用户Tom，位于dc=cscw下面的ou=Users下，所以第一行写的是ou=Users,dc=cscw

![netstat -anptl](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/openldap-1.png)

<h2 id="IdP"> 3.2 布署IdP</h2>

### 3.2.1 环境
IDP版本：2.4.4

操作系统：Ubuntu12.04 64bit

### 3.2.2 安装IdP


#### 3.2.2.1安装oracle jdk
依次输入下面的4条命令：
```
sudo apt-get install python-software-properties
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java7-installer
```

#### 3.2.2.2安装apache及tomcat7
依次输入下面的4条命令：
```
sudo apt-get install apache2
sudo a2enmod ssl
sudo a2enmod proxy_ajp
sudo apt-get install tomcat7
```

#### 3.2.2.3配置apache和tomcat

**(1)更改本机域名**

输入下面的命令：
```
sudo vi /etc/hosts  
```

加入下面的内容：
```
127.0.0.1	idp.edx.org	shibboleth
```
把idp.edx.org换成你的IdP机器的域名

**(2)更改apache ServerName**

输入下面的命令：
```
sudo vi /etc/apache2/apache2.conf
```

加入下面的内容：
```
ServerName idp.edx.org
```
把idp.edx.org换成你的IdP机器的域名

**(3)设置JAVA_OPTS 环境变量**

输入下面的命令：

```
sudo vi /etc/init.d/tomcat7  
```

找到JAVA_OPTS ，添加参数：-XX:+UseG1GC -Xmx1500m -XX:MaxPermSize=128m 

如下图所示：

![picture](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/idp-install-2.png)

**(4)设置POST提交限制**

输入下面的命令：
```
sudo vi /etc/tomcat7/server.xml  
```

找到 Connector ,添加属性maxPostSize ，设置值为100K(100000)

如下图：

![picture](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/idp-install-3.png)

**(5)使用Context Deployment Fragment**

输入下面的命令：

```
sudo vi /etc/tomcat7/Catalina/localhost/idp.xml 
```

输入下面的命令创建文件 *TOMCAT_HOME*/conf/Catalina/localhost/idp.xml （*TOMCAT_HOME* 是你的tomact安装路径，这里是/etc/tomcat7）
```
sudo vi /etc/tomcat7/Catalina/localhost/idp.xml

```
在新建的文件idp.xml中添加下面的内容：
```
<Context docBase="/opt/shibboleth-idp/war/idp.war"
         privileged="true"
	 antiResourceLocking="false"
	 antiJARLocking="false"
	 unpackWAR="false"
	 swallowOutput="true"
	 cookies="false" />
```

#### 3.2.2.4 安装IdP
输入下面的命令：
```
sudo wget http://shibboleth.net/downloads/identity-provider/2.4.4/shibboleth-identityprovider-2.4.4-bin.zip
sudo unzip shibboleth-identityprovider-2.4.4-bin.zip
cd shibboleth-identityprovider-2.4.4
sudo JAVA_HOME=/usr/lib/jvm/java-7-oracle ./install.sh
sudo chown -R tomcat6:tomcat6 /opt/shibboleth-idp
```

安装过程中安装路径不用改。hostname改为：idp.edx.org。(把idp.edx.org换成你的IdP机器的域名),会要求设置密码：这里设为shibboleth.如下图所示：

![picture](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/idp-install-5.png)
![picture](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/idp-install-6.png)

检查IdP是否安装成功，访问：http://idp.edx.org:8080/idp/profile/Status 把idp.edx.org换成你设置的hostname ，如果输出OK则说明安装正确

![picture](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/idp-install-8.png)

图片中Status文件的内容是OK

如果出现错误,请查看日志:/opt/shibboleth-idp/logs/idp-process.log

[官方的问题解答列表](https://wiki.shibboleth.net/confluence/display/SHIB2/NativeSPTroubleshootingCommonErrors#NativeSPTroubleshootingCommonErrors-Unabletolocatemetadataforidentityprovider(https://identities.supervillain.edu/idp/shibboleth).)


### 3.2.3 配置IdP与OpenLdap连接

#### 3.2.3.1 在配置前,请使用test_ldap.py保证LDAP正常工作。

在IdP机器上运行[test_ldap.py](https://github.com/jennyzhang8800/os_platform/blob/master/backup/shibboleth-idp/idp/test_ldap.py)脚本。test_ldap.py脚本内容如下：

```
import ldap

ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
l = ldap.initialize("ldap://192.168.1.138")
l.set_option(ldap.OPT_REFERRALS, 0)
l.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
l.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
l.set_option( ldap.OPT_X_TLS_DEMAND, True )
l.set_option( ldap.OPT_DEBUG_LEVEL, 255 )
baseDN = "ou=Users,dc=cscw"
searchScope = ldap.SCOPE_SUBTREE
retrieveAttributes = None
searchFilter = "cn=*Tom*"
ldap_result_id = l.search(baseDN, searchScope, searchFilter)
result_set = []
while 1:
    result_type, result_data = l.result(ldap_result_id, 0)
    if (result_data == []):
        break
    else:
        if result_type == ldap.RES_SEARCH_ENTRY:
            result_set.append(result_data)
    print result_set
```

把上图中的
+ l = ldap.initialize("ldap://192.168.1.138")   中的192.168.1.138改为openldap的IP
+ baseDN = "ou=Users,dc=cscw"  改为你的baseDN
+ searchFilter = "cn=*Tom*"    *Tom*改为dc=cscw ou=Users下的一个用户名

在IdP机器上运行test_ldap.py后应该返回用户名为Tom的一些属性信息（这些属性就是3.1.5中创建用户Tom时所设置的属性）。如下图所示：

![picture-test_ldap.py](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/test_ldap.py%E7%BB%93%E6%9E%9C.png)

如果能正常获得上图所示的用户信息，则说明ldap正常工作，可以进行配置ldap验证了，通过以下步骤实现：

#### 3.2.3.2 属性定义attribute-resolver.xml

输入下面的命令：

`sudo vi /opt/shibboleth-idp/conf/attribute-resolver.xml`

(1)在Attribute Definitions下面加入下面的内容：

```
<resolver:AttributeDefinition xsi:type="ad:Simple" id="uid" sourceAttributeID="uid">
        <resolver:Dependency ref="myLDAP" />
        <resolver:AttributeEncoder xsi:type="enc:SAML1String" name="urn:mace:dir:attribute-def:uid" />
        <resolver:AttributeEncoder xsi:type="enc:SAML2String" name="urn:oid:0.9.2342.19200300.100.1.1" friendlyName="uid" />
    </resolver:AttributeDefinition>

    <resolver:AttributeDefinition xsi:type="ad:Simple" id="email" sourceAttributeID="mail">
        <resolver:Dependency ref="myLDAP" />
        <resolver:AttributeEncoder xsi:type="enc:SAML1String" name="urn:mace:dir:attribute-def:mail" />
        <resolver:AttributeEncoder xsi:type="enc:SAML2String" name="urn:oid:0.9.2342.19200300.100.1.3" friendlyName="mail" />
    </resolver:AttributeDefinition>

<resolver:AttributeDefinition xsi:type="ad:Simple" id="commonName" sourceAttributeID="cn">
    <resolver:Dependency ref="myLDAP" />
    <resolver:AttributeEncoder xsi:type="enc:SAML1String" name="urn:mace:dir:attribute-def:cn" />
    <resolver:AttributeEncoder xsi:type="enc:SAML2String" name="urn:oid:2.5.4.3" friendlyName="cn" />
</resolver:AttributeDefinition>

<resolver:AttributeDefinition xsi:type="ad:Simple" id="eppn" sourceAttributeID="eduPersonPrincipalName">
    <resolver:Dependency ref="myLDAP" />
    <resolver:AttributeEncoder xsi:type="enc:SAML1String" name="urn:mace:dir:attribute-def:eduPersonPrincipalName" />
    <resolver:AttributeEncoder xsi:type="enc:SAML2String" name="urn:oid:1.3.6.1.4.1.5923.1.1.1.6" friendlyName="eppn" />
</resolver:AttributeDefinition>

```

如下图所示：

![idp-ldap-conf-0](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/idp-ldap-conf-0.png)


(2)取消下面内容的注释，并修改参数：

```
<resolver:DataConnector id="myLDAP" xsi:type="dc:LDAPDirectory"
    ldapURL="ldap://192.168.1.138:389" 
    baseDN="ou=Users,dc=cscw" 
    principal="cn=admin,dc=cscw"
    principalCredential="1234567">
    <dc:FilterTemplate>
        <![CDATA[
            (uid=$requestContext.principalName)
        ]]>
    </dc:FilterTemplate>
    </resolver:DataConnector>
```

+ 第二行 192.168.1.138:389 ， 改为 你的ldap的IP地址加上端口号389 ,  注意：如果你用的是http协议，一定不能把端口号389省去！
+ 第三行 baseDN 改为你存放的用户在ldap中的baseDN
+ 第四行 principal 改为登录ldap时的Login DN (如3.1.5的图片所示的Login DN)
+ 第五行 principalCredential 改为登录ldap时的密码（如3.1.5的图片所示的Password）


#### 3.2.3.3 更改attribute-filter.xml

输入下面的命令:

`sudo vi /opt/shibboleth-idp/conf/attribute-filter.xml`

加入下面的内容：

```
<afp:AttributeRule attributeID="uid">
    <afp:PermitValueRule xsi:type="basic:ANY" />
</afp:AttributeRule>

<afp:AttributeRule attributeID="email">
    <afp:PermitValueRule xsi:type="basic:ANY" />
</afp:AttributeRule>

<afp:AttributeRule attributeID="commonName">
    <afp:PermitValueRule xsi:type="basic:ANY" />
</afp:AttributeRule>

<afp:AttributeRule attributeID="eppn">
    <afp:PermitValueRule xsi:type="basic:ANY" />
</afp:AttributeRule>
```
如下图所示：

![picture-idp-ldap-conf-2](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/idp-ldap-conf-2.png)


#### 3.2.3.4 更改handler.xml

输入下面的命令：

`sudo vi /opt/shibboleth-idp/conf/handler.xml`

取消下面内容的注释：

```
<!--  Username/password login handler -->
<ph:LoginHandler xsi:type="ph:UsernamePassword"
    jaasConfigurationLocation="file:///opt/shibboleth-idp/conf/login.config">
<ph:AuthenticationMethod>urn:oasis:names:tc:SAML:2.0:ac:classes:
    PasswordProtectedTransport</ph:AuthenticationMethod>
</ph:LoginHandler></code>
```

注释下面的内容：

```
<ph:LoginHandler xsi:type="ph:RemoteUser">
        <ph:AuthenticationMethod>urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified</ph:AuthenticationMethod>
    </ph:LoginHandler>
```

```
 <ph:LoginHandler xsi:type="ph:PreviousSession">
        <ph:AuthenticationMethod>urn:oasis:names:tc:SAML:2.0:ac:classes:PreviousSession</ph:AuthenticationMethod>
    </ph:LoginHandler>
```

如下图所示：

![idp-ldap-conf-3](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/idp-ldap-conf-3.png)

#### 3.2.3.5 更改login.config

输入下面的命令：

`sudo vi /opt/shibboleth-idp/conf/login.config`

取消下面内容的注释：
```
edu.vt.middleware.ldap.jaas.LdapLoginModule required
    ldapUrl="ldap://192.168.1.138:389"
    baseDn="ou=Users,dc=cscw"
    ssl="false"
    //userFilter="uid={0}";
    userField="uid";
```

如下图所示：

![idp-ldap-conf-5](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/idp-ldap-conf-5.png)

#### 3.2.3.6 测试idp 与ldap 连接是否正常

运行aacli.sh 脚本可测试两者连接是否正常

输入下面的命令：

```
cd /opt/shibboleth-idp/bin
export JAVA_HOME=/usr/lib/jvm/java-7-oracle
./aacli.sh --configDir=/opt/shibboleth-idp/conf/ --principal=Tom

```
可以看到下图所示的结果，即ldap返回的Tom用户的有关属性（uid,cn,eppn,mail） 以及属性的值(Tom,Tom,yannizhang8800@163.com,yannizhang8800@163.com),如果能返回这些信息，说明idp与ldap能正常连接。
![idp-conf-6](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/idp-conf-6.png)



<h2 id="SP-edx"> 3.3 布署Open edX端的SP</h2>



下面是在Open edX机器上进行的配置，参考的是[官方配置文档](http://edx.readthedocs.io/projects/edx-installing-configuring-and-running/en/latest/configuration/tpa/index.html) ,通过以下步骤实现：
### 3.3.1 打开第三方认证特性

由于默认情况下open edx的第三方认证是不可用的，因此首先需要打开第三方认证特性。通过下面的操作实现：

(1)输入下面的命令：
```
sudo su  
vi /edx/app/edxapp/lms.env.json 
```
(2)在lms.env.json文件中，把
"ENABLE_COMBINED_LOGIN_REGISTRATION" 和 "ENABLE_THIRD_PARTY_AUTH"
这两个属性的值都改为true，保存修改。
```
"FEATURES" : {
    ...
    "ENABLE_COMBINED_LOGIN_REGISTRATION": true,
    "ENABLE_THIRD_PARTY_AUTH": true
}
```

如下图所示:
![open-edx-sp-conf-0](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-0.png)

### 3.3.2 配置Open edX作为SP
 首先生成credential key pair（即生成公钥和私钥）以保证SP和IDP之间数据传输的安全性，然后利用credential key pair生成SP端的原数据。
 
#### 3.3.2.1 生成公钥和私钥
（1）输入下面的命令：
```
openssl req -new -x509 -days 3652 -nodes -out saml.crt -keyout saml.key
```
(2)   输入要求填写的信息(Country Name, state or Province Name,等)，就会在当前路径下生成公钥saml.crt和私钥saml.key

如下图所示：

![open-edx-sp-conf-1](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-1.png)

生成结果如下：生成公钥saml.crt和私钥saml.key

![open-edx-sp-conf-2](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-2.png)

#### 3.3.2.2 把生成的公钥和私钥添加到LMS配置文件中
（1）打开lms.auth.json文件

输入下面的命令：
```
vi /edx/app/edxapp/lms.auth.json  
```

（2）把saml.crt文件的内容复制到SOCIAL_AUTH_SAML_SP_PUBLIC_CERT属性中。

 **注意：** saml.crt文件的内容去掉开头和结尾的注释，内容去掉换行。使之为一个单行的字符串添加入SOCIAL_AUTH_SAML_SP_PUBLIC_CERT属性中。
 
 saml.crt文件内容如下图：
 
 ![open-edx-sp-conf-3](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-3.png)
 
  lms.auth.json加入公钥私钥内容后如下：
  
   ![open-edx-sp-conf-4](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-4.png)
   
（3）把saml.key文件的内容复制到SOCIAL_AUTH_SAML_SP_PRIVATE_KEY属性中。

  saml.key内容如下。也是只复制中间的内容（内容去掉开头和结尾的注释，内容去掉换行。使之为一个单行的字符串）
   
   ![open-edx-sp-conf-5](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-5.png)
   
#### 3.3.2.3 配置open edx作为SP，生成原数据

**（1）登录到Django 管理界面。**

URL为http://{your_URL}/admin ，如这里的是:http://cherry.os.cs.tsinghua.edu.cn/admin

界面如下图：输入有管理员权限的用户名密码

   ![open-edx-sp-conf-6](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-6.png)
   
 登录成功后，看到如下的界面：
 
 ![open-edx-sp-conf-7](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-7.png)
 
**（2）在Third_Party_Auth下面的SAML Configuration 中点击Add.**

如下图：

 ![open-edx-sp-conf-8](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-8.png)
 
**（3）选中Enabled，输入下面的信息：**
    
+ **Entity ID**: 这会作为生成的原数据中的entity_id。一般输入服务器名，如： http://saml.mydomain.com/. （我这里的是http://cherry.os.cs.tsinghua.edu.cn）

+ **Site**: 指定作为SP的站点

+ **Organization Info**: 组织信息，如下，把下面改为你的edx信息
```
{
   "en-US": {
       "url": "http://www.mydomain.com",
       "displayname": "{Complete Name}",
       "name": "{Short Name}"
   }
}
```
改为：
```
{
   "en-US": {
       "url": "http://cherry.os.cs.tsinghua.edu.cn",
       "displayname": "Tsinghua University",
       "name": "tsinghua"
   }
}
```

+ **Other config str**: 定义IdP原数据文件的安全设置，保持默认即可。如下：
```
{
   "SECURITY_CONFIG": {
     "signMetadata": false,
     "metadataCacheDuration": ""
   }
}
```
点右下角的保存按钮,如下图所示：

 ![open-edx-sp-conf-9](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-9.png)
 
  ![open-edx-sp-conf-10](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-10.png)
  
保存后结果如下图:
 
  ![open-edx-sp-conf-11](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-11.png)

**（4）在 {your LMS URL}/auth/saml/metadata.xml 中可以看到生成的SP端原数据**

如我这里的是：http://cherry.os.cs.tsinghua.edu.cn/auth/saml/metadata.xml

如下图所示：

 ![open-edx-sp-conf-12](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-12.png)
 
原数据的内容在IdP配置的时候会用到。

如果上面的步骤中没有生成成功原数据，在3.3.2.2做完后先重启edx服务，然后再进行3.3.2.3

重启edx服务的命令如下：

```
sudo /edx/bin/supervisorctl restart edxapp:   
sudo /edx/bin/supervisorctl restart edxapp_worker:   
```
#### 3.3.2.4 确保SAML 认证后端己加载

如果你没有改过/edx/app/edxapp/lms.env.json文件的设置（向它添加过THIRD_PARTY_AUTH_BACKENDS设置），这一步可以什么都不过，跳过就行。

### 3.3.3 使SP和IdP结合

#### 3.3.3.1交换原数据

(1) 先把3.3.2.3中生成的SP端原数据，保存到IdP端


我这里把http://cherry.os.cs.tsinghua.edu.cn/auth/saml/metadata.xml 的内容保存为单独的文件，命名为edx-metadata.xml


然后把edx-metadata.xml 拷贝到IdP机器中的/opt/shibboleth-idp/metadata/目录下。


(2)更改IdP配置文件relying-party.xml

在IdP机器输入下面的命令：

```
vi /opt/shibboleth-idp/conf/relying-party.xml   
```
在Metadata Configuration的部分加入面的内容：
```
<metadata:MetadataProvider xsi:type="FilesystemMetadataProvider"
                xmlns="urn:mace:shibboleth:2.0:metadata" id="SPMETADATA-EDX"
                metadataFile="/opt/shibboleth-idp/metadata/edx-metadata.xml" />
```

（你也可以不上传原数据文件到IdP机器，直接在把上面的 metadataFile="/opt/shibboleth-idp/metadata/edx-metadata.xml" 改为
metadataFile="http://cherry.os.cs.tsinghua.edu.cn/auth/saml.metadata.xml"
)

如下图：
 
 ![open-edx-sp-conf-13](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-13.png)
  
 (3) 把IdP原数据（位于IdP机器中的/opt/shibboleth-idp/metadata/目录下，一般为idp-metadata.xml文件），保存到一个可以用URL获得的地方。
 
我这里把IdP原数据保存到gitlab仓库中,链接为：https://raw.githubusercontent.com/jennyzhang8800/os_platform/master/idp-metadata.xml

#### 3.3.3.2 添加并使SAML IdP可用

**（1）登录到Django 管理界面。**

 管理界面的URL，如http://cherry.os.cs.tsinghua.edu.cn/admin
 
**（2）在Third_Party_Auth下的Provider Configuration(SAML IdPs) 点击Add**

 如下图：
 
   ![open-edx-sp-conf-14](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-14.png)
   
 **(3)输入下面的信息：**
 
+ **Icon class**: 这里输入fa-university.
+ **Name** 在登录页面出现的IdP名。如：Tsinghua_OS.
+ **Secondary**: 选中这一项则在登录时会有一个中间页列表出现。这里选中
+ **Backend name**: 默认为tpa-saml,不用改
+ **Site**: 站点名，输入edx的站点名。如：cherry.cs.tsinghua.edu.cn
+ **IdP slug**: 唯一识别这个IdP的名称。不含空格，可以作为CSS类名。如：shibboleth
+ **Entity ID**: 与IdP原数据（idp-metadata.xml）中的entity_id值保持一致（一定要一致！）。如：http://os.cs.tsinghua.edu.cn/idp/shibboleth
+ **Metadata source**: IdP原数据的URL。如：在3.1.2中我们己经有了：https://raw.githubusercontent.com/jennyzhang8800/os_platform/master/idp-metadata.xml

把Ship email verification 和Visible勾上。（可选）  

其他项可以不用填

在右上角：Enabled选中

右下角：点Save保存。

 ![open-edx-sp-conf-15](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-15.png)
  
 ![open-edx-sp-conf-16](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-16.png)
    
保存后结果如下图所示：

 ![open-edx-sp-conf-17](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-17.png)
  

 
    
### 3.3.4 检测是否配置成功
 
 (1). 在管理界面（http://cherry.os.cs.tsinghua.edu.cn/admin），进入到Third_Party_Auth下的Provider Configuration(SAML IdPs)界面。查看Metadata Ready是否是绿色的勾，如果是测说明能够正确获取IdP原数据。
 
![open-edx-sp-conf-18](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-18.png)
 
 如果不是绿色的勾，先重启edx服务，然后刷新页面。 如果还不行，请检查Metadata source是否正确，通过这个URL是不是能获取idp原数据。

(2).检查是否能正确获取IdP端原数据的另一个方法，点击Third_Parth_Auth下的SAML Provider Data选项，会获取一次原数据，如果能成功获取，Is valid会打上绿色的勾。

如下图：

![open-edx-sp-conf-19](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-19.png)
  
  结果如下：（Is valid）打上绿色勾，说明能正确获取IdP端的原数据
  
![open-edx-sp-conf-20](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-20.png)
    
 (3) 登录
 
在open edx首页，点sign in 

  
![open-edx-sp-conf-21](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-21.png)

点击Use my Institution/Campus credentials

    
 ![open-edx-sp-conf-22](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-22.png)
 
 点击Tsinghua_OS(你设置的名称)
 
![open-edx-sp-conf-23](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-23.png)
  
  跳到IdP页面，输入用户名密码进行登录。（用户名密码是在open ldap保己经创建好用户的）
  
![open-edx-sp-conf-24](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-24.png)
    
 如果是第一次登录，账号没有在edx注册过，那么会跳到下面的页面。以后登录会直接跳到edx页面，不会再出现下面的页面
 ![open-edx-sp-conf-26](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-conf-26.png)
 
登录成功，返回到edx页面。

![open-edx-sp-conf-25](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/open-edx-sp-config-25.png)

<h2 id="SP-gitlab"> 3.4 布署Gitlab端的SP</h2>



### 3.4.1 安装及配置SP
#### 3.4.1.1 安装Apache上的shib模块
输入下面的命令：
```
sudo apt-get install libapache2-mod-shib2
a2enmod shib2
```
访问/Shibboleth.sso/Status, 若能显示信息,则一切正常

#### 3.4.1.2 配置SP
要修改的配置文件都位于/etc/shibboleth目录下

**(1)修改shibboleth2.xml**

输入下面的命令：
```
sudo su
vi /etc/shibboleth/shibboleth2.xml
```
+ 修改sp的entityID为你SP的域名
```
<ApplicationDefaults entityID="http://apple.cs.tsinghua.edu.cn"
                     REMOTE_USER="eppn persistent-id targeted-id">
```
将上述代码中的http://apple.cs.tsinghua.edu.cn 改为你的gitlab域名

+ 添加 sso

```
<SSO entityID="http://os.cs.tsinghua.edu.cn/idp"
             discoveryProtocol="SAMLDS" discoveryURL="https://ds.example.org/DS/WAYF">
          SAML2 SAML1
</SSO>
```

将上述代码中的http://os.cs.tsinghua.edu.cn/idp 改为你的idp域名

+ 添加 session initiator

```
<SessionInitiator type="Chaining" Location="/Login" isDefault="true" id="Intranet"
    relayState="cookie" entityID="http://os.cs.tsinghua.edu.cn/idp/shibboleth" forceAuthn="true">
    <SessionInitiator type="SAML2" acsIndex="1" template="bindingTemplate.html"/>
    <SessionInitiator type="Shib1" acsIndex="5"/>
</SessionInitiator>
```

将上述代码中的http://os.cs.tsinghua.edu.cn/idp 改为你的idp域名


**(2)生成原数据文件**

通过以下步骤生成原数据文件sp-metadata.xml

+ 生成密钥

输入下面的命令：(将第二条命令中的apple.cs.tsinghua.edu.cn换成你的gitlab域名)
```
cd /etc/shibboleth
shib-keygen -h apple.cs.tsinghua.edu.cn
```

+ 利用密钥生成原数据文件 sp-metadata.xml

输入下面的命令：(将命令中的apple.cs.tsinghua.edu.cn换成你的gitlab域名)
```
shib-metagen -h apple.cs.tsinghua.edu.cn> /etc/shibboleth/sp-metadata.xml
```


可以看到在/etc/shibboleth目录下生成了SP端的原数据文件sp-metadata.xml

**(3)交换IdP和SP的原数据文件**

+ 在SP端修改shibboleth2.xml,在shibboleth2.xml中加入下面的代码：
```
<MetadataProvider type="XML" file="idp-metadata.xml"/>
```

+ 在IdP端进行配置与SP连接

在IdP端对与SP连接的配置只需两步：
  
第一步：把SP端的原数据拷贝到IdP端的/opt/shibboleth-idp/metadata目录下

在SP端运行下面的命令：（把下面代码中的username 换成IdP机器的用户名，idp-ip换成IdP机器的IP地址。）
```
scp sp-metadata.xml username@idp-ip:/opt/shibboleth-idp/metadata

```
然后到IdP端运行下面的命令：
```
chown tomcat7:tomcat7 sp-metadata.xml
```


如果直接运行上面代码没有权限直接持贝，则可采取下面的方法 ：

在SP机器输入面的命令：
```
scp sp-metadata.xml zyni@192.168.1.137:/home/zyni
```
再到IdP机器输入下面的命令：
```
cp /home/zyni/sp-metadata.xml /opt/shibboleth-idp/metadata
chown tomcat7:tomcat7 sp-metadata.xml
```

第二步：修改relying-party.xml

在IdP端输入下面的命令：
```
vi /opt/shibboleth-idp/conf/relying-party.xml
```
在"Metadata Configuration"部分，加入下面的代码：
```
<metadata:MetadataProvider xsi:type="FilesystemMetadataProvider"
    xmlns="urn:mace:shibboleth:2.0:metadata" id="SPMETADATA"
    metadataFile="/opt/shibboleth-idp/metadata/sp-metadata.xml" />
```
如下图所示：
![idp-sp-metadata-config](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/idp-sp-metadta-config.png)


**(4)配置属性映射文件attribute-map.xml**

输入下面的命令：
```
vi /etc/shibboleth/attribute-map.xml
```

注释下面的代码：
```
<!--
<Attribute name="urn:oid:1.3.6.1.4.1.5923.1.1.1.6" id="eppn">
    <AttributeDecoder xsi:type="ScopedAttributeDecoder"/>
</Attribute>
-->
```
添加下面的代码：
```
<Attribute name="urn:oid:1.3.6.1.4.1.5923.1.1.1.6" id="eppn"/>
<Attribute name="urn:oid:2.5.4.3" id="cn"/>
<Attribute name="urn:oid:0.9.2342.19200300.100.1.3" id="mail"/>
```
**(4)修改attribute-policy.xml**

注释下面的代码：
```
<afp:AttributeRule attributeID="eppn">
    <afp:PermitValueRuleReference ref="ScopingRules"/>
</afp:AttributeRule>
```


### 3.4.2 配置apache(default)
以下内容参考[官方文档](https://gitlab.com/gitlab-org/gitlab-ce/blob/master/doc/integration/shibboleth.md)

(1) 将/etc/apache2/sites-available/default 文件用下面的内容替换：

```
<VirtualHost *:80>
  ServerName apple.cs.tsinghua.edu.cn
  ServerSignature Off

  ProxyPreserveHost On

  # Ensure that encoded slashes are not decoded but left in their encoded state.
  # http://doc.gitlab.com/ce/api/projects.html#get-single-project
  AllowEncodedSlashes NoDecode

  <Location />
    # New authorization commands for apache 2.4 and up
    # http://httpd.apache.org/docs/2.4/upgrading.html#access
    Order allow,deny
    Allow from all
    ProxyPassReverse http://127.0.0.1:8080/
    ProxyPassReverse http://apple.cs.tsinghua.edu.cn/
  </Location>

  <Location /users/auth/shibboleth/callback>
    AuthType shibboleth
    ShibRequestSetting requireSession 1
    ShibUseHeaders On
    require valid-user
  </Location>

  Alias /shibboleth-sp /usr/share/shibboleth
  <Location /shibboleth-sp>
    Satisfy any
  </Location>

  <Location /Shibboleth.sso>
    SetHandler shib
  </Location>
  #apache equivalent of nginx try files
  # http://serverfault.com/questions/290784/what-is-apaches-equivalent-of-nginxs-try-files
  # http://stackoverflow.com/questions/10954516/apache2-proxypass-for-rails-app-gitlab
  RewriteEngine on
  RewriteCond %{DOCUMENT_ROOT}/%{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_URI} !/Shibboleth.sso
  RewriteCond %{REQUEST_URI} !/shibboleth-sp
  RewriteRule .* http://127.0.0.1:8080%{REQUEST_URI} [P,QSA]
  RequestHeader set X_FORWARDED_PROTO 'http'
  # needed for downloading attachments
  DocumentRoot /opt/gitlab/embedded/service/gitlab-rails/public

  #Set up apache error documents, if back end goes down (i.e. 503 error) then a maintenance/deploy page is thrown up.
  ErrorDocument 404 /404.html
  ErrorDocument 422 /422.html
  ErrorDocument 500 /500.html
  ErrorDocument 503 /deploy.html

  LogFormat "%{X-Forwarded-For}i %l %u %t \"%r\" %>s %b" common_forwarded
  ErrorLog  /var/log/apache2/gitlab.err.log
  CustomLog /var/log/apache2/gitlab.acces.log "combined"       
 
	ServerAdmin webmaster@localhost

	DocumentRoot /var/www
	<Directory />
		Options FollowSymLinks
		AllowOverride None
	</Directory>
	<Directory /var/www/>
		Options Indexes FollowSymLinks MultiViews
		AllowOverride None
		Order allow,deny
		allow from all
	</Directory>

	ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
	<Directory "/usr/lib/cgi-bin">
		AllowOverride None
		Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
		Order allow,deny
		Allow from all
	</Directory>

	ErrorLog ${APACHE_LOG_DIR}/error.log

	# Possible values include: debug, info, notice, warn, error, crit,
	# alert, emerg.
	LogLevel warn

	CustomLog ${APACHE_LOG_DIR}/access.log combined

    Alias /doc/ "/usr/share/doc/"
    <Directory "/usr/share/doc/">
        Options Indexes MultiViews FollowSymLinks
        AllowOverride None
        Order deny,allow
        Deny from all
        Allow from 127.0.0.0/255.0.0.0 ::1/128
    </Directory>

</VirtualHost>

```

把上述代码中的：
```
 ServerName apple.cs.tsinghua.edu.cn
 ProxyPassReverse http://apple.cs.tsinghua.edu.cn/
```
这两个地方的apple.cs.tsinghua.edu.cn 改为你的gitlab域名。

改完之后保存

(2)激活使用的apache模块

输入下面的命令：
```
a2enmod proxy
a2enmod rewrite
a2enmod headers
a2enmod proxy_http
```

(3)重启apache服务

输入下面的命令：
```
sudo service apache2 restart
```

### 3.4.3 配置Gitlab与SP连接(gitlab.rb)

输入下面的命令：
```
vi /etc/gitlab/gitlab.rb
```
修改如下配置：

```
external_url 'https://apple.cs.tsinghua.edu.cn'


# disable Nginx
nginx['enable'] = false

    gitlab_rails['omniauth_allow_single_sign_on'] = true
    gitlab_rails['omniauth_block_auto_created_users'] = false
    gitlab_rails['omniauth_enabled'] = true
    gitlab_rails['omniauth_providers'] = [
      {
            "name" => 'shibboleth',
            "args" => {
            "shib_session_id_field" => "HTTP_SHIB_SESSION_ID",
            "shib_application_id_field" => "HTTP_SHIB_APPLICATION_ID",
            "uid_field" => 'HTTP_EPPN',
            "name_field" => 'HTTP_CN',
            "info_fields" => { "email" => 'HTTP_MAIL'}
            }
      }
    ]
```

上述代码主要是三个地方的改动：
+ 把external_url 改为你的gitlab外部访问域名
+ 禁用gitlab默认的nginx代理服务器
+ 启用sso

更改后保存，然后输入下面的命令使配置生效：
```
sudo gitlab-ctl reconfigure
```

### 3.4.4 结果演示

**(1)进入gitlab首页，点Shibboleth按钮**

http://apple.cs.tsinghua.edu.cn

可以看到"Sign in with Shibboleth" ,点击“Shibboleth”按钮。

![gitlab-demo-0](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/gitlab-demo-0.png)


**(2)跳转到IdP登录页面登录**

当点击了“Shibboleth”按钮之后，会跳转到IdP页面登录，输入openLdap中存在的用户名密码，点击登录

![gitlab-demo-1](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/gitlab-demo-1.png)

**(3)登录成功返回到gitlab**

IdP认证通过后，自动返回到gitlab,此时己登录进入gitlab

![gitlab-demo-2](https://github.com/jennyzhang8800/os_platform/blob/master/pictures/gitlab-demo-2.png)
