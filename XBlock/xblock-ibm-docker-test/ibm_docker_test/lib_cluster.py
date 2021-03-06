__author__ = 'zyu'

import datetime
import json
import requests
from lib_util import Util
import time


class ClusterHelper(object):

    logger = Util.ibm_logger()
    base_url = "https://crl.ptopenlab.com:8800/restful/supernova"

    def __init__(self, conf_id, num,token,username,pwd):
        #self.logger.info("ClusterHelper.__init__")
        self._conf_id = conf_id
        self._num = num
	#self._token = token
	#self._username = username
	#self._pwd = pwd
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": token,
            "username": username,
            "password": pwd
        }

    def cluster_create(self):
        url = self.base_url + "/cluster/create"
        body = json.dumps({                        
            "cluster_config_id": self._conf_id,
            "cluster_number"   : self._num,
        })
	
        ret = requests.post(url,headers=self._headers, data=body)
	ret = json.loads(ret.text)
        return ret

    def cluster_list(self):
        url = self.base_url + "/cluster/list"
        ret = requests.get(url,headers=self._headers)
        ret = json.loads(ret.text)
        return ret

    def cluster_delete(self,cluster_id):
        url = self.base_url + "/cluster/delete/{0}".format(cluster_id)
        ret = requests.delete(url,headers=self._headers)
        ret = json.loads(ret.text)
        return ret

    def cluster_show(self,cluster_id):
        #url = self.base_url + "/cluster/show/{0}".format(cluster_id)
        url = self.base_url + "/cluster/show/" + cluster_id
        ret = requests.get(url,headers=self._headers)
        ret = json.loads(ret.text)
        return ret

    def get_webshell(self,user_Authorization,ip):
        headers = {
        "Content-Type": "application/json",
        "Authorization": user_Authorization
        }
        url = "https://dashboard.ptopenlab.com:443/restful/supernova/web_shell/get/Beijing/" + ip
        ret = requests.get(url,headers=headers)
        ret = json.loads(ret.text)
	return ret



if __name__ == "__main__":
    cluster = ClusterHelper("fd1caddb-96cf-4e16-ab0b-2b34a3b4f51a", 1,
                             "Token 12fd33018268c5e144da368af5085acde9319e34",
                             "xyongcn@qq.com",
                             "21b^54X3dafa2#37a")
    ret = cluster.cluster_create()
    time.sleep(20)
    cluster_id = ret["clusters"][0]["id"]
    print cluster_id
    print cluster.cluster_show(cluster_id)
    #if ret["success"] == True:
    #    print "OK"
    #else:
    #    print "ERROR"

