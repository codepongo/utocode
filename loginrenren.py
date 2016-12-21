# -*- coding: utf-8 -*-
import urllib2
import cookielib
import urllib
import re
import sys
cj = cookielib.CookieJar()
print cj
print '---------------visit-------------------'
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
url='http://wap.renren.com/'
req = urllib2.Request(url)
html = opener.open(req)
reg = re.compile('''^.*<form.*action="(?P<url>[^"]*).*'''
                 '''<input.*name="origURL" value="(?P<origURL>[^"]*).*'''
                 '''<input.*name="lbskey" value="(?P<lbskey>[^"]*).*'''
                 '''<input.*name="c"[ ]*value="(?P<c>[^"]*).*'''
                 '''<input.*name="pq"[ ]*value="(?P<pq>[^"]*).*'''
                 '''<input.*name="ref"[ ]*value="(?P<ref>[^"]*).*'''
                 '''<input.*name="login"[ ]*value="(?P<login>[^"]*).*'''
                 )
response = html.read()
regMatch = reg.match(response)
url = regMatch.group('url')
origURL_value = regMatch.group('origURL')
lbskey_value = regMatch.group('lbskey')
c_value = regMatch.group('c')
pq_value = regMatch.group('pq')
ref_value = regMatch.group('ref')
# sina email
email_value = sys.argv[1]
# simple password
password_value = sys.argv[2]
login_value = regMatch.group('login')
print cj

print '-----------------login-------------------'
post_data = 'origURL=' + origURL_value + '&'
post_data += 'lbskey='+ lbskey_value + '&'
post_data += 'c=' + c_value + '&'
post_data += 'pq=' + pq_value + '&'
post_data += 'ref=' + ref_value + '&'
post_data += 'email=' + email_value + '&'
post_data += 'password=' + password_value + '&'
post_data += 'login=' + login_value + '&'
req = urllib2.Request(url, post_data)
html = opener.open(req)
print html.read().decode('utf8')
print cj
