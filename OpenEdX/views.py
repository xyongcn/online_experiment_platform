#add content to /edx/app/edxapp/edx-platform/common/djangoapps/student/views.py
#add by zyu
import re
import pymongo
import string
import random
import ldap 
import ldap.modlist as modlist
import requests
import smtplib
from email.mime.text import MIMEText
import datetime
from Crypto.Cipher import AES

# add by zyu,for IBM account init
def account_init(request):
    usrid = request.GET.get('usrid')
    email = request.GET.get('email')

    #check if student is user on xuetang
    try:
        code = CheckID(usrid)
    except Exception:
	return HttpResponse(u'<p>request failed,please try again</p>')
    if code == 404:
	return HttpResponse(u'<p>user error</p>')
    #check referrer
    referrer=request.META.get('HTTP_REFERER')
    if referrer.startswith('http://www.xuetangx.com/courses/course-v1:TsinghuaX+30240243X_2015_T2+2015_T2') == False:
	return HttpResponse(u'<p>request error</p>')

    #check email
    if len(email) <= 7:
	return HttpResponse(u'email format error</p>')
    if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) == None:
	return HttpResponse(u'email format error</p>')

    #check id,no api for check now,just judge the length
    if len(usrid) != 32:
	return HttpResponse(u'xuetang id error')
    #check if user has been inited
    conn = pymongo.Connection('localhost', 27017)
    db = conn.test
    db.authenticate("user","secret")
    ibm = db.ibm
    result = ibm.find_one({"usrid":usrid})
    if result:
	password = result["password"]
	name = result["name"]
	response = "<p>you have initialized ibm account ,your account info:</p>"
        response += "<p>IBM supernova account:</p><p style='color:red'>" + email + "</p>"
        response += "<p>shibboleth account(for edx and gitlab):</p><p style='color:red'>" + name + "</p>"
        response += "<p>password:</p><p style='color:red'>" + password + "</p>"
        conn.disconnect()

        return HttpResponse(response)
    else:
        #generate user name
        name = generate_name()
	#generate random password
	password = GenPassword(8)
	#encrypt password by AES
	#obj = AES.new('secret12345678', AES.MODE_CBC, 'This is an IV456')
        ibm.insert({"usrid":usrid, "name":name, "email":email, "password":password})
        conn.disconnect()
	log.info("IBM account init usrid: %s , name: %s , email: %s",usrid,name,email)
	#create ldap account
	CreateLdapAccount(name,password,email)
	log.info("Create LDAP account for %s",email)
	#create ibm account
	result = CreateIBMAccount(email,password)
	response = "<p>Create Success,your account info:</p>"
	response += "<p>IBM supernova account:</p><p style='color:red'>" + email + "</p><p>" + result + "</p>"
	response += "<p>shibboleth account(for edx and gitlab):</p><p style='color:red'>" + name + "</p>"
	response += " <p>password:</p><p style='color:red'>" + password + "</p>"
	return HttpResponse(response)

#add by zyu
def ibm_password_reset_request(request):
    usrid = request.GET.get('usrid','default')
    email = request.GET.get('email','default')

    #check user info
    #check if student is user on xuetang
    try:
        code = CheckID(usrid)
    except Exception:
	return HttpResponse(u'<p>request failed,please try again</p>')
    if code == 404:
	return HttpResponse(u'<p>user identity error</p>')
    #check referrer
    #referrer=request.META.get('HTTP_REFERER')
    #if referrer.startswith('http://www.xuetangx.com/courses/') == False:
    #	 print "request error"
    #	 return

    #check email
    if len(email) <= 7:
	return HttpResponse(u'<p>email format error</p>')
    if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) == None:
	return HttpResponse(u'<p>email format error</p>')

    #check whether user has have a token ,insert if not
    conn = pymongo.Connection('localhost', 27017)
    db = conn.test
    db.authenticate("user","secret")
    ibm = db.ibm
    result = ibm.find_one({"usrid":usrid,"email":email})
    if not result:
	return HttpResponse(u'<p>sorry,you do not have a shibboleth account yet</p>')
    passwd_reset = db.passwd_reset
    result = passwd_reset.find_one({"usrid":usrid,"email":email})
    if result:
	expiration_time = result["expiration_time"]
        #not expired yet
	if datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") <= expiration_time:
	    return HttpResponse(u'<p>failed,you already have a link to reset password and the link has not expired</p>')
	#expired ,delete it
	else:
	    passwd_reset.remove({"usrid":usrid,"email":email})

    #generate verify code
    vcode = uuid.uuid4().get_hex()[16:]
    #expirate after one day
    expiration_time = (datetime.datetime.now() + datetime.timedelta(days = 1)).strftime("%Y-%m-%d %H:%M:%S") 

    passwd_reset.insert({"usrid":usrid,"email":email,"vcode":vcode,"expiration_time":expiration_time})

    #send passwd to user's email
    mailto_list=[email]
    mail_host="smtp.126.com"
    mail_user="zhangyu911"
    mail_pass="secret"
    mail_postfix="126.com"

    content="<p>hello,the link below will be expired 24 hour later. \n " 
    content += "</p>" + "\n<a href='http://crl.ptopenlab.com:8811/openedx/ibm/password_reset?usrid=" + usrid + "&vcode=" + vcode +"'>click here to reset your shibboleth password</a>"

    sub="mooc OS:reset password of shibboleth for os"
    msg = MIMEText(content,_subtype='html',_charset='utf-8')
    msg["Accept-Language"]="zh-CN"
    msg["Accept-Charset"]="ISO-8859-1,utf-8"
    msg['Subject'] = sub
    me="hello"+"<"+mail_user+"@"+mail_postfix+">"
    msg['From'] = me
    msg['To'] = ";".join(mailto_list)

    try:
    	s = smtplib.SMTP_SSL()
    	s.connect(mail_host,465)
    	s.login(mail_user,mail_pass)
    	s.sendmail(me, mailto_list, msg.as_string())
    	s.close()
    except Exception, e:
        log.info(str(e))
	return HttpResponse('<p>send email failed:' + str(e) + '</p>')

    return HttpResponse(u'<p>the link has been sent to your email,please check it</p>')

@csrf_exempt
def ibm_password_reset(request):
    log.info(str(request))
    #both get and post
    usrid = request.REQUEST.get('usrid','default')
    vcode = request.REQUEST.get('vcode','default')
    if usrid == 'default' or vcode == 'default':
	return render_to_response('password_reset_message.html', {'message':'error request'})
    #check user info
    #check if student is user on xuetang
    try:
        code = CheckID(usrid)
    except Exception:
	return render_to_response('password_reset_message.html', {'message':'request failed,please try again'})
    if code == 404:
	return render_to_response('password_reset_message.html', {'message':'user identity error'})

    #check whether the token is valid
    conn = pymongo.Connection('localhost', 27017)
    db = conn.test
    db.authenticate("user","secret")
    passwd_reset = db.passwd_reset
    result = passwd_reset.find_one({"usrid":usrid,"vcode":vcode})
    if not result:
	return render_to_response('password_reset_message.html', {'message':'error request'})

    expiration_time = result["expiration_time"]
    #vcode has expired
    if datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") > expiration_time:
	passwd_reset.remove({"usrid":usrid,"vcode":vcode})
	return render_to_response('password_reset_message.html', {'message':'the url is invalid!,you should reset password in 24 hours'})

    if not request.POST.has_key("new_pwd"):
	context = {'usrid':usrid,'vcode':vcode,'error':''}
	return render_to_response('password_reset.html', context)

    
    email = request.POST.get('email','default')
    new_pwd = request.POST.get('new_pwd','default')
    #check email
    ibm = db.ibm
    result = ibm.find_one({"usrid":usrid,"email":email})
    if not result:
        conn.disconnect()
	context = {'usrid':usrid,'vcode':vcode,'error':'email error'}
        return render_to_response('password_reset.html', context)
    #check password
    if len(new_pwd)<8:
        conn.disconnect()
	context = {'usrid':usrid,'vcode':vcode,'error':'password too short ,at least 8'}
        return render_to_response('password_reset.html', context)

    name = result["name"]
    #start modify user password
    try:
        ModifyLdapPwd(name,new_pwd)
    except ldap.LDAPError, error:
        conn.disconnect()
	return render_to_response('password_reset_message.html', {'message':'reset failed with ldap :'+str(error)})

    #update mongodb
    passwd_reset.remove({"usrid":usrid,"vcode":vcode})
    #obj = AES.new('secret12345678', AES.MODE_CBC, 'This is an IV456')
    #ibm.update({"usrid":usrid,"email":email},{"$set":{"password":obj.encrypt(new_pwd).encode('hex')}})
    ibm.update({"usrid":usrid,"email":email},{"$set":{"password":new_pwd}})
    conn.disconnect() 
    return render_to_response('password_reset_message.html', {'message':'password modified successfully'})

def generate_name():                                                                                                          
    conn=pymongo.Connection('localhost', 27017)
    db = conn.test                                                                                                            
    db.authenticate('user','secret')
    global_var=db.global_var.find_and_modify(query={}, update={"$inc":{ 'user_count': 1 }}, upsert=False, full_response= True)
    count = global_var["value"]["user_count"]
    username = "s%04d" % count
    return username

def CheckID(id):
    r = requests.get('http://www.xuetangx.com/internal_api/check_anonymous?anonymous_id=' + id, headers={
                        'XUETANGX-API-KEY': 'secret_token'})
    return r.status_code


def GenPassword(length):
    numOfNum = random.randint(1,length-1)
    numOfLetter = length - numOfNum
    slcNum = [random.choice(string.digits) for i in range(numOfNum)]
    slcLetter = [random.choice(string.ascii_letters) for i in range(numOfLetter)]
    slcChar = slcNum + slcLetter
    random.shuffle(slcChar)
    genPwd = ''.join([i for i in slcChar])
    return genPwd

def CreateLdapAccount(username,password,email):
    ldap_url = "ldap://10.9.17.245:389"
    principal_name = "cn=admin,dc=edx,dc=com"
    ldap_password  = "secret"
    base_dn = "ou=Users,dc=edx,dc=com"
    l = ldap.initialize(ldap_url) 
    l.bind(principal_name, ldap_password) 
    dn= "uid=" + username + "," + base_dn

    attrs = {}
    attrs['objectclass'] = ['top','inetOrgPerson','eduPerson']
    attrs['cn'] = str(username)
    attrs['sn'] = str(username)
    attrs['givenName'] = str(username)
    attrs['uid'] = str(username)
    attrs['userPassword'] = str(password)
    attrs['description'] = 'ldap user for shibboleth'
    attrs['eduPersonPrincipalName'] = str(email)
    attrs['mail'] = str(email)
    # Convert our dict to nice syntax for the add-function using modlist-module
    ldif = modlist.addModlist(attrs)
    l.add_s(dn,ldif)
    l.unbind_s()

def ModifyLdapPwd(name,new_pwd):
    ldap_url = "ldap://10.9.17.245:389"
    principal_name = "cn=admin,dc=edx,dc=com"
    ldap_password  = "secret"
    base_dn = "ou=Users,dc=edx,dc=com"
    l = ldap.initialize(ldap_url) 
    l.bind(principal_name, ldap_password) 
    dn= "uid=" + name + "," + base_dn
	
    mod_attrs = [(ldap.MOD_REPLACE,'userPassword',str(new_pwd))]
    l.modify_s(dn, mod_attrs)

def CreateIBMAccount(email,password):
    headers = {

        "Content-Type": "application/json",

        "Authorization": "Token secret

    }



    ret = requests.post("https://dashboard.ptopenlab.com:443/restful/supernova/user/register",

                        headers=headers, data=json.dumps({

                            "user_name": email,

                            "password": password,

                        }))
    log.info("Create IBM account username: %s, password: %s status code: %d, response: %s",email,password,ret.status_code,ret.text)

    return ret.text
