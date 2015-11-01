该XBlock用于为用户分配IBM所提供的docker资源,并定时或由用户手动回收

1.修改hosts,否则api无法访问url

  vi /etc/hosts
  #add the following code
  172.16.10.120 crl.ptopenlab.com
