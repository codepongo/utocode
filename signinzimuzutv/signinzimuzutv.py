import poster
import cookielib
import urllib
import urllib2
import sys
import json

def login(email, password):
    cookie = cookielib.LWPCookieJar('cookie.txt')
    opener = poster.streaminghttp.register_openers()
    opener.add_handler(urllib2.HTTPCookieProcessor(cookie))

    req = urllib2.Request('http://www.zimuzu.tv/User/Login/ajaxLogin',
            urllib.urlencode({'account':email, 
                'password':password, 
                'remember':1,
                'url_back':'http://www.zimuzu.tv/user/sign'}))
    req.add_header('Referer', 'http://www.zimuzu.tv/user/login')
    rep = urllib2.urlopen(req).read()
    cookie.save()
    return json.loads(rep)['info']
def sign():
    req = urllib2.Request('http://www.zimuzu.tv/user/sign')
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
    print sign()
    print logout()
