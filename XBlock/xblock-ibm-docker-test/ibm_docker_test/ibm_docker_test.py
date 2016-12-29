__author__ = 'zyu'
import json
import thread
import datetime
import re
import pymongo
import time
from threading import Timer

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, List, Boolean
from xblock.fragment import Fragment

from config import Config
from lib_cluster import ClusterHelper
from lib_docker import DockerHelper
from lib_git import GitLabUtil
from lib_model import Cluster
from lib_util import Util

class IBMDockerTestXBlock(XBlock):

    logger = Util.ibm_logger()

    is_new = Boolean(default=True, scope=Scope.user_state, help="is new")
    is_empty = Boolean(default=True, scope=Scope.user_state, help="do not have docker")
    private_key = String(default="", scope=Scope.user_state, help="SHH Private Key")
    public_key = String(default="", scope=Scope.user_state, help="SHH Public Key")
    cluster_id = String(default="", scope=Scope.user_state, help="user cluster id")
    git_id = Integer(default="", scope=Scope.user_state, help="Git id")
    #repo url may be different from username/repo.git,so get it from api
    git_name = String(default="", scope=Scope.user_state, help="git repo")
    ldap_name = String(default="", scope=Scope.user_state, help="ldap name")
    ldap_pwd = String(default="", scope=Scope.user_state, help="ldap password")
    #student only own one cluster
    clusters = List(default=[], scope=Scope.user_state, help="clusters")

    # config
    CONFIG = Config.CONFIG
    git_host = CONFIG["GIT"]["HOST"]
    git_port = CONFIG["GIT"]["PORT"]
    git_admin_token = CONFIG["GIT"]["ADMIN_TOKEN"]
    git_import_url  = CONFIG["GIT"]["IMPORT_URL"]
    git_project_name  = CONFIG["GIT"]["PROJECT_NAME"]
    git_teacher_token = CONFIG["GIT"]["TEACHER"]["TOKEN"]

    cluster_conf_id = CONFIG["CLUSTER"]["CLUSTER_CONFIG_ID"]
    cluster_num = CONFIG["CLUSTER"]["CLUSTER_NUM"]
    delete_time = CONFIG["CLUSTER"]["DELETE_TIME"]
    init_user = CONFIG["CLUSTER"]["INIT_USER"]
    init_pwd  =  CONFIG["CLUSTER"]["INIT_PWD"]

    ibm_username = CONFIG["IBM_ACCOUNT"]["ACCOUNT"]
    ibm_pwd      = CONFIG["IBM_ACCOUNT"]["PASSWORD"]

    mongo_admin = CONFIG["MONGO"]["ADMIN"]
    mongo_pwd   = CONFIG["MONGO"]["PASSWORD"]

    user_Authorization    = CONFIG["AUTHORIZATION"]["USER"]
    cluster_Authorization = CONFIG["AUTHORIZATION"]["CLUSTER"]

    cluster_helper = ClusterHelper(cluster_conf_id,cluster_num,cluster_Authorization,ibm_username,ibm_pwd)
    docker_helper  = DockerHelper(git_host,init_user,init_pwd)


    def student_view(self, context=None):

        # runtime error
        if not hasattr(self.runtime, "anonymous_student_id"):
            return self.message_view("Error in ibm_docker (get anonymous student id)" + "Cannot get anonymous_student_id in runtime", None)

        # preview in studio
        if self.runtime.anonymous_student_id == "student":
	    cluster_list = []

	    conn=pymongo.Connection('localhost', 27017)
            db = conn.test
	    db.authenticate(self.mongo_admin,self.mongo_pwd)
            cluster=db.cluster
	    for i in cluster.find():
		new_cluster = Cluster()
		new_cluster.set_name(i["cluster_name"])
		new_cluster.set_user(i["username"])
		new_cluster.set_id(i["cluster_id"])
		new_cluster.set_creation_time(i["creation_time"])
		new_cluster.set_status(i["status"])
		new_cluster.set_ip(i["ip"])
		cluster_list.append(new_cluster.object_to_dict())

            context_dict = {
                "clusters": cluster_list,
                "message": ""
            }
            fragment = Fragment()
            fragment.add_content(Util.render_template('static/html/ibm_clusters.html', context_dict))
            fragment.add_css(Util.load_resource("static/css/ibm_docker.css"))
            #fragment.add_javascript(Util.load_resource("static/js/src/uc_lab.js"))
            fragment.initialize_js("IBMDockerTestXBlock")
            return fragment

	student = self.runtime.get_real_user(self.runtime.anonymous_student_id)
        email = student.email
        name = student.first_name + " " + student.last_name
        username = student.username

        # temporary code ,not used in next course
	conn=pymongo.Connection('localhost', 27017)
        db = conn.test
	db.authenticate(self.mongo_admin,self.mongo_pwd)
        token=db.token
	result = token.find_one({"username":username})
	conn.disconnect()

	#I dont now why the cluster cannot be shown in page directly
	temp_clusters = self.clusters

        if self.is_new and not result:
            # create git account when first visiting

	    # get teacher id
	    #result, message = GitLabUtil.get_user(self.git_host, self.git_port, self.git_teacher_token)
	    #self.logger.info("get teacher id")
	    #self.logger.info(result)
	    #self.logger.info(message)
            #if not result:
            #    return self.message_view("Error in get teacher info")
            #try:
	    #    message = json.loads(message)
            #    teacher_id = message["id"]
            #except Exception:
            #    return self.message_view("Error in uc_docker (load json string)", message, context)

	    #add teacher to developer
	    #result, message = GitLabUtil.add_project_developer(self.git_host, self.git_port, self.git_user_token, username, self.git_project_name, teacher_id)
	    #self.logger.info("add developer result:")
            #self.logger.info(result)
            #self.logger.info(message)
            #if not result:
            #    return self.message_view("Error in uc_docker (add teacher to developer)", message, context)
	    conn=pymongo.Connection('localhost', 27017)
            db = conn.test
	    db.authenticate(self.mongo_admin,self.mongo_pwd)
	    ibm = db.ibm
	    result = ibm.find_one({"email":email})
	    if not result:
		return self.message_view("Error in ibm_docker (get shibboleth account info). detail" + message, temp_clusters)

	    self.ldap_name = result["name"]
	    self.ldap_pwd  = result["password"]

	    #get user id by email
	    result, message = GitLabUtil.get_userid(self.git_host, self.git_port, self.git_admin_token,self.ldap_name)    
	    self.logger.info("get user id result:")
            self.logger.info(result)
            self.logger.info(message)
	    if not result:
                return self.message_view("Error in ibm_docker (get user id). detail" + message, temp_clusters)
	    self.git_id = message["id"]
	    self.save()

            result, message = GitLabUtil.create_project(self.git_host, self.git_port, self.git_admin_token, self.git_import_url, 				                                   self.git_project_name,self.git_id)
            self.logger.info("add project result:")
            self.logger.info(result)
            self.logger.info(message)
            if not result:
                return self.message_view("Error in ibm_docker (add project). detail:" + message, temp_clusters)

	    try:
                conn=pymongo.Connection('localhost', 27017)
                db = conn.test
	 	db.authenticate(self.mongo_admin,self.mongo_pwd)
                token=db.token
		result = token.find_one({"username":username})
	        if not result:
		    self.private_key, self.public_key = Util.gen_ssh_keys(email)
                    #self.logger.info("private_key:" + self.private_key)
                    self.save()
                    token.insert({"username":username,"private_key":self.private_key,"public_key":self.public_key})
		else:
		    self.private_key = result["private_key"]
		    self.public_key  = result["public_key"]
		    self.save()
                conn.disconnect()

            except Exception, ex:
                return self.message_view("Error in ibm_docker (gen ssh key). detail:" + ex, context)

            result, message = GitLabUtil.add_ssh_key(self.git_host, self.git_port, self.git_admin_token, "ucore default", 								self.public_key,self.git_id)
            self.logger.info("add_ssh_key result:")
            self.logger.info(result)
            self.logger.info(message)
            if not result:
                return self.message_view("Error in ibm_docker (add git ssh key). detail:" + message, temp_clusters)

            self.is_new = False
            self.save()

        context_dict = {
            "dockers": self.clusters,
            "message": "",
            "report":""
        }
        fragment = Fragment()
        fragment.add_content(Util.render_template('static/html/ibm_docker.html', context_dict))
        fragment.add_css(Util.load_resource("static/css/ibm_docker.css"))
        fragment.add_javascript(Util.load_resource("static/js/src/ibm_docker.js"))
        fragment.initialize_js("IBMDockerTestXBlock")
        return fragment


    def message_view(self, message, clusters):
        context_dict = {
            "dockers": clusters,
            "message": str(message),
            "report":""
        }
        fragment = Fragment()
        fragment.add_content(Util.render_template('static/html/ibm_docker.html', context_dict))
        fragment.add_css(Util.load_resource("static/css/ibm_docker.css"))
        fragment.add_javascript(Util.load_resource("static/js/src/ibm_docker.js"))
        fragment.initialize_js("IBMDockerTestXBlock")
        return fragment


    @XBlock.json_handler
    def create_docker(self, data, suffix=""):
  
	if self.is_empty == True:    
	    ret = self.cluster_helper.cluster_create()
	    if ret["success"] == False:
	        return {"result": False, "message": ret["messages"]}

	    self.cluster_id = ret["clusters"][0]["id"]
	    self.is_empty = False
	    cluster_name = ret["clusters"][0]["name"]
	    cluster_status = "creating"
	    cluster_creation_time = datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d %H:%M:%S")

	    cluster = Cluster()
	    cluster.set_id(self.cluster_id)
	    cluster.set_name(cluster_name)
	    cluster.set_status(cluster_status)
	    cluster.set_creation_time(cluster_creation_time)
	    self.clusters.append(cluster.object_to_dict())
	    self.save()
	    time.sleep(40)		
	
	#create cluster is a asynchronous api,so we should read status constantly to get ip
	#if user already have docker,the code below will update docker info
	for i in range(60):
	    try:
	        ret = self.cluster_helper.cluster_show(self.cluster_id)
	    except Exception:
                #self.logger.info("fail to get ip,cluster id: " + self.cluster_id + " should try again")
		if i == 59:
		    return {"result": False, "message": "time out to get ip"}
		time.sleep(10)
		continue
	        
	    if ret["success"] == False:
		self.clear_docker_info()
	        return {"result": False, "message": ret["messages"]}
	    if ret["status"] == "CREATE_FAILED":
		self.clear_docker_info()
		return {"result": False, "message": "docker create failed"}
	    if ret["status"] == "CREATE_COMPLETE":
		break
	    time.sleep(10)

	cluster_ip = ret["ext_ip"]
	self.clusters[0]["ip"] = cluster_ip
	self.clusters[0]["status"] = "CREATE_COMPLETE"

	#get webshell url
	#get webshell url,may be failed with service or name unknown
	for i in range(10):
	    try:
		ret = self.cluster_helper.get_webshell(self.user_Authorization,cluster_ip)
		if ret["success"] == False:
	            return {"result": False, "message": ret["messages"]}
		break
	    except Exception:
                #self.logger.info("fail to get webshell ,should try again")
		if i == 9:
		    return {"result": False, "message": "time out to get webshell"}
		time.sleep(1)
		continue
	
	self.clusters[0]["webshell"] = ret["url"]
	self.save()
	
	student = self.runtime.get_real_user(self.runtime.anonymous_student_id)
        username = student.username
	email = student.email

        conn=pymongo.Connection('localhost', 27017)
        db = conn.test
	db.authenticate(self.mongo_admin,self.mongo_pwd)
        cluster = db.cluster
        result = cluster.find_one({"cluster_id":self.clusters[0]["id"]})
	if not result:
	    cluster_name = self.clusters[0]["name"]
	    cluster_id = self.clusters[0]["id"]
	    creation_time = self.clusters[0]["creation_time"]
	    ip = self.clusters[0]["ip"]
	    status = self.clusters[0]["status"]
            cluster.insert({"username":username,"cluster_name":cluster_name,"cluster_id":cluster_id,"creation_time":creation_time,"ip":ip,"status":status})      
            self.logger.info("username:"+username + " create cluster,cluster_name:" + cluster_name + " cluster_id:" + cluster_id+" creation_time:" + creation_time + " ip" + ip + " status: " + status) 
	
	    #start timer to delete docker after 4 hours
	    t=Timer(self.delete_time*3600,auto_delete_docker,(self,))
	    t.start()

	    # initialize docker
	    # get user's name and pwd in ldap
	    ibm = db.ibm
	    result_ibm = ibm.find_one({"email":email})
	    if not result_ibm:
		return {"result": False, "message": "fail to get shibboleth account info"}

	    self.ldap_name = result_ibm["name"]
	    self.ldap_pwd = result_ibm["password"]
	
	    #wait for docker to start
            time.sleep(10)
	    for i in range(20):
	        try:
		    self.docker_helper.init_user(ip,self.ldap_name,self.ldap_pwd)
		    break
	        except Exception:
                    self.logger.info("fail to get ssh to docker,should try again")
		    if i == 19:
		        return {"result": False, "message": "time out to initialize docker"}
		    time.sleep(5)
		    continue
	    #get private and public key to initialize git config
	    token=db.token
 	    result_token = token.find_one({"username":username})
	    if not result_token: 
		return {"result": False, "message": "initialize git config in docker failed,could not find private key"}
	    
	    try:
	    #get user repo url,should place the code below on line 154,but for some reason place here temporarily
	        result_git, message = GitLabUtil.get_userid(self.git_host, self.git_port, self.git_admin_token,self.ldap_name)
	        if not result_git:
                    return {"result": False, "message": "fail to get user repo url"}
	        self.git_name = message["username"]
	        self.save()
	        self.docker_helper.init_git(ip,self.ldap_name,self.ldap_pwd,email,self.git_name,result_token["private_key"],result_token["public_key"])
	    except Exception:
	    	return {"result": False, "message": "fail to initialize docker"}

	conn.disconnect()
        return {"result": True}


    @XBlock.json_handler
    def delete_docker(self, data, suffix=""):
 	if self.is_empty == True:
	    return {"result": False, "message": "you do not have docker now"}
	ret = self.cluster_helper.cluster_delete(self.cluster_id)
	#if docker has been deleted because of time out,just clear docker info
	if ret["success"] == False:
	    self.clear_docker_info()
	    self.is_empty == True
	    ret = ret["messages"]
            ret = json.loads(ret)                                                                                         
            code = ret["code"]
	    if code == 404:
		return {"result": True, "message": "clear docker info,docker has been deleted"}
	    else:    
	        return {"result": False, "message": ret["messages"]}

	student = self.runtime.get_real_user(self.runtime.anonymous_student_id)
        username = student.username

        conn=pymongo.Connection('localhost', 27017)
        db = conn.test
	db.authenticate(self.mongo_admin,self.mongo_pwd)
        cluster=db.cluster
        cluster.remove({"username":username,"cluster_id":self.clusters[0]["id"]})      
        conn.disconnect()

        self.logger.info("username:"+username + " delete cluster,cluster_name" + self.clusters[0]["name"] + " cluster_id" + self.clusters[0]["id"]+" creation_time" + self.clusters[0]["creation_time"] + " cluster_ip" + self.clusters[0]["ip"])
	temp_cluster_id = self.cluster_id
	self.clear_docker_info()
	self.is_empty == True
	time.sleep(30)
        code = 0
        #update cluster status,there are some problems in api,you should delete several times
        for i in range(8):
            ret = self.cluster_helper.cluster_delete(temp_cluster_id)                                                         
            try:
                ret = ret["messages"]
                ret = json.loads(ret)                                                                                         
                code = ret["code"]
            except Exception:
                time.sleep(8)
                continue
            if code == 404:#then the cluster is really deleted
                break
	if code != 404:
	    self.clear_docker_info()
	    self.is_empty == True
	    return {"result": False, "message": "delete failed"}
        return {"result": True}

    #reset user's docker info
    def clear_docker_info(self):
	self.clusters = []
	self.is_empty = True
	self.cluster_id = ""

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("IBMDockerXBlock", """<vertical_demo><ibm_docker/></vertical_demo>"""),
        ]

#the function is separate,cannot set value from xblock
def auto_delete_docker(xb):
    student = xb.runtime.get_real_user(xb.runtime.anonymous_student_id)
    username = student.username
    if xb.is_empty == True:
        return 
    ret = xb.cluster_helper.cluster_delete(xb.cluster_id)
    if ret["success"] == False:
        xb.logger.info("auto timer delete failed " + username + "may be docker has been deleted")

    conn=pymongo.Connection('localhost', 27017)
    db = conn.test
    db.authenticate(xb.mongo_admin,xb.mongo_pwd)
    cluster=db.cluster
    cluster.remove({"username":username,"cluster_id":xb.clusters[0]["id"]})      
    conn.disconnect()

    xb.logger.info("username:"+username + " auto delete cluster,cluster_name" + xb.clusters[0]["name"] + " cluster_id" + xb.clusters[0]["id"]+" creation_time" + xb.clusters[0]["creation_time"] + " cluster_ip" + xb.clusters[0]["ip"])
    #del xb.clusters[0]
    #xb.is_empty = True
    #temp_cluster_id = xb.cluster_id
    #xb.cluster_id = ""
	
    time.sleep(30)
    code = 0
    #update cluster status,there are some problems in api,you should delete several times
    for i in range(8):
        ret = xb.cluster_helper.cluster_delete(xb.cluster_id)                                                         
        try:
            ret = ret["messages"]
            ret = json.loads(ret)                                                                                         
            code = ret["code"]
        except Exception:
            time.sleep(8)
            continue
        if code == 404:#then the cluster is really deleted
            break
    if code != 404:
        xb.logger.info("auto timer delete failed,time out " + username)
	return
    xb.logger.info("auto timer delete success " + username)
