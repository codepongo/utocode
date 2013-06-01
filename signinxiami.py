# -*- coding: utf-8 -*-
import urllib2
import cookielib
import urllib
import re
import sys
import HTMLParser

post = {}
host = 'http://www.xiami.com'
user_agent = 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.57 Safari/537.17'
def index(opener, url):
    """visit http://m.xiami.com"""
    post = {}
    req = urllib2.Request(url, headers={"User-Agent":user_agent})
    html = opener.open(req).read().decode('utf-8')
    class Index(HTMLParser.HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag == 'form':
                for attr in attrs:
                    if attr[0] == 'action':
                        post['url'] = attr[1]
            if tag == 'input':
                propertys = {}
                for attr in attrs:
                    propertys[attr[0]] = attr[1]
                if 'name' in propertys.keys() and propertys['name'] == 'LoginButton':
                    post['submit'] = propertys['value']
                    return
    Index().feed(html)

    return post

def login(opener, post):
    """login"""
    data = 'email=' + urllib.quote(post['email']) + '&'
    data += 'password=' + urllib.quote(post['password']) + '&'
    data += 'LoginButton=' + urllib.quote(post['submit'].encode('utf-8'))
    try:
        req = urllib2.Request(post['url'], data, headers={"User-Agent":user_agent})
    except urllib2.HTTPError, e:
        print 'login request is failed [errorno = %s]' % e.code
        exit(0)
    html = opener.open(req).read()
    if html.find(u'退出'.encode('utf-8')) != -1:
        return html
    else:
        print 'login is failed'
        exit(0)

def info(html):
    begin = html.find('已连续签到')
    if begin != -1:
        msg = html[begin:]
        end = msg.find('</div>')
        return msg[:end]
    else:
        return None

def turn2index(opener, html):
    web = []
    """turn to index page"""
    class Profile(HTMLParser.HTMLParser):
        def handle_data(self, data):
            if data == '首页':
                    index = self.get_starttag_text()
                    web.append(index.replace('<a href="', '').replace('">', ''))
    Profile().feed(html)
    if len(web) == 0:
        url = 'http://www.xiami.com/web'
    else:
        url = web[0]
    try:
        req = urllib2.Request(url, headers={"User-Agent":user_agent})
    except urllib2.HTTPError, e:
        print 'turn2index request is failed [errorno = %s]' % e.code
        exit(0)
    html = opener.open(req).read()
    return html

def signin(opener, html):
    """sigin"""
    signin = []

    class SignIn(HTMLParser.HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                propertys = {}
                for attr in attrs:
                    propertys[attr[0]] = attr[1]
                if 'class' in propertys.keys() and propertys['class'] == 'check_in':
                    signin.append(propertys['href'])

    SignIn().feed(html)
    if len(signin) == 0:
        msg = info(html)
        if msg is not None:
            return msg.decode('utf-8')
        else:
            print('the url to signin is not found')
            exit(0)
    try:
        req = urllib2.Request(host+signin[0], headers={"User-Agent":user_agent})
    except urllib2.HTTPError, e:
        print e.code
        exit(0)
    req.add_header('Referer', 'http://www.xiami.com/web')
    html = opener.open(req).read()
    msg = info(html)
    if msg is not None:
        return msg.decode('utf-8')
    else:
        print 'signin info is not found. SignIn is failed'
        exit(0)

def logout(opener, url):
    """logout"""
    req = urllib2.Request(url, headers={"User-Agent":user_agent})
    html = opener.open(req).read()
    if html.find('退出') != -1:
        print 'logout is failed'
        print 'req=', req
        print 'html=', html.decode('utf-8')
        exit(0)
    return


if __name__ == '__main__':
    httpHandler = urllib2.HTTPHandler(debuglevel=1)
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    post = index(opener, 'http://m.xiami.com')
    post['url'] = host + post['url']
    while True:
        post['email'] = raw_input('email:')
        if post['email'] is '':
            break
        post['password'] = raw_input("%s 's password:" % post['email'])
        html = login(opener, post)
        html = turn2index(opener, html)
        print signin(opener, html)
        logout(opener, host+'/member/logout?from=mobile')
