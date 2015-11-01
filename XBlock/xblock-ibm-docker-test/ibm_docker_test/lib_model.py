import datetime


class Cluster(object):

    def __init__(self):
        self._name = "unknown"
	self._user = ""
	self._id = ""
        self._creation_time = "unknown"
        self._status = "wait for create"
	self._ip = "wait..."
	self._webshell = ""

    def object_to_dict(self):
        dic = dict(
            name=self._name,
	    user=self._user,
	    id=self._id,
            creation_time=self._creation_time,
            status=self._status,
	    ip=self._ip,
	    webshell=self._webshell)
        return dic

    @staticmethod
    def dict_to_object(dic):
        obj = CLUSTER()
        obj.name = dic["name"]
	obj.user = dic["user"]
	obj.id = dic["id"]
        obj.creation_time = dic["creation_time"]
        obj.status = dic["status"]
        obj.ip = dic["ip"]
	obj.webshell = dic["webshell"]
        return obj

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_user(self):
        return self._user

    def set_user(self, user):
        self._user = user

    def get_id(self):
        return self._id

    def set_id(self, id):
        self._id = id

    def get_creation_time(self):
        return self._creation_time

    def set_creation_time(self, value):
        self._creation_time = value

    def get_status(self):
        return self._status

    def set_status(self, value):
        self._status = value

    def get_ip(self):
        return self._ip

    def set_ip(self, value):
        self._ip = value

    def get_webshell(self):
        return self._webshell

    def set_webshell(self, value):
        self._webshell = value

    name = property(get_name, set_name)
    user = property(get_user, set_user)
    creation_time = property(get_creation_time, set_creation_time)
    status = property(get_status, set_status)
    ip = property(get_ip, set_ip)
    webshell = property(get_webshell, set_webshell)


class User(object):
    def __init__(self):
        self._name = ""
        self._git_id = 0

    def get_name(self):
        return self._name

    def set_name(self, value):
        self._name = value

    def get_git_id(self):
        return self._git_id

    def set_git_id(self, value):
        self._git_id = value

    name = property(get_name, set_name)
    git_id = property(get_git_id, set_git_id)

    def object_to_dict(self):
        dic = dict(
            name=self._name,
            git_id=self._git_id)
        return dic

    @staticmethod
    def dict_to_object(dic):
        obj = User()
        obj.name = dic["name"]
        obj.git_id = dic["git_id"]
        return obj


class Teacher(User):
    def __init__(self):
        User.__init__(self)

    @staticmethod
    def dict_to_object(dic):
        obj = Teacher()
        obj.name = dic["name"]
        obj.git_id = dic["git_id"]
        return obj
