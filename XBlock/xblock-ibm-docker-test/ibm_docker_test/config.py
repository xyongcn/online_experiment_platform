class Config:

    CONFIG = {
        "GIT":
        {
            # GitLab's host and port, make sure open-edx can access
            "HOST" : "172.16.13.236",
            "PORT" : 80,
	    # fork the repo from Github or other supported websites
	    "IMPORT_URL" : "https://github.com/chyyuu/ucore_os_lab",
	    "PROJECT_NAME" : "ucore_lab",
            # GitLab admin account's token
            "ADMIN_TOKEN": "secret",

            # Teacher account information, be used to create repo/project
            "TEACHER":
            {
                "TOKEN": "secret"
            }
        },

        "CLUSTER":
        {

            # cluster_config_id for create cluster
            "CLUSTER_CONFIG_ID": "secret",

            #number of cluster for every student
            "CLUSTER_NUM"   : 1,

	    #time to auto-delete docker(hour)
	    "DELETE_TIME"   : 4,

            #user paramiko to init user info

            "INIT_USER"    : "secret",
            "INIT_PWD"     : "secret",
        },
	"MONGO":
	{
	    "ADMIN"     :"secret",
	    "PASSWORD"  :"secret"
	},
	"IBM_ACCOUNT":
	{
	    "ACCOUNT"     :"xyongcn@qq.com",
	    "PASSWORD"    :"secret"
	},
	"AUTHORIZATION":
	{
	    "USER"	  :"TOKEN secret", #for getting webshell
	    "CLUSTER"     :"TOKEN secret"  #for creating cluster
	}
    }
