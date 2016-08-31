import cookielib
import urllib
import urllib2
import sys
import json
import os
import time
cookie_file = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'cookie.txt')
def login(email, password):
    cookie = cookielib.LWPCookieJar(cookie_file)
    opener = urllib2.build_opener()
    urllib2.install_opener(opener)
    opener.add_handler(urllib2.HTTPCookieProcessor(cookie))
    req = urllib2.Request('http://www.zimuzu.tv/User/Login/ajaxLogin',
            urllib.urlencode({'account':email, 
                'password':password, 
                'remember':1,
                'url_back':'http://www.zimuzu.tv/user/user'}))
    req.add_header('Referer', 'http://www.zimuzu.tv/user/login')
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko')
    rep = urllib2.urlopen(req).read()
    cookie.save()
    return json.loads(rep)['info']
def sign(referer):
    req = urllib2.Request('http://www.zimuzu.tv/user/sign')
    req.add_header('Referer', referer)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko')
    req.add_header('Host', 'www.zimuzu.tv')
    rep = urllib2.urlopen(req).read()
    start = rep.find('<div class="a2 tc">')
    end = rep.find('<div class="a2 tc"><span class="f2">')
    result = rep[start:end]
    result = result.replace('<div class="a2 tc">', '').replace('<font class="f3">','').replace('</font>', '').replace(' <font class="f2">', '').replace('</div>', '')
    if sys.platform == 'win32':
        result = result.decode('utf8')
    return result
def logout():
    rep = urllib2.urlopen(urllib2.Request('http://www.zimuzu.tv/user/logout/ajaxLogout')).read()
    return json.loads(rep)['info']

if __name__ == '__main__':
    print login(sys.argv[1], sys.argv[2])
    time.sleep(5)
    print sign('http://www.zimuzu.tv')
    time.sleep(5)
    print sign('http://www.zimuzu.tv/user/user')
    time.sleep(5)
    print sign('http://www.zimuzu.tv/user/sign')
    time.sleep(5)
    print logout()
    os.remove(cookie_file)
