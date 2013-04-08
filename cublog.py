"""cublog.py

blog.chinaunix.net blog python client script
more than http://blog.chinaunix.net/uid-24789255-id-114279.html

"""
import sys
import os
import xmlrpclib
class MetaWeblog:
    def __init__(self, url, usr, passwd):
        self.user = usr
        self.password = passwd
        self.server = xmlrpclib.ServerProxy(url)
        print self.getUserBlogs()
        self.userid = self.getUserBlogs()[0]['blogid']

    def getUserId(self):
        return self.userid
    def newPost(self, title, description):
        blog = self.getRecentPosts('1')[0]
        blog['title'] = title
        blog['content'] = description
        blog['description'] = description
        blog['categories'] = [blog['categories'][0]['classname']]
#        blog['postid'] = ''
        return self.server.metaWeblog.newPost(self.userid, self.user, self.password, blog, True)
    def getPost(self, postid=''):
        return self.server.metaWeblog.getPost(postid, self.user, self.password)
    def getRecentPosts(self, count='9999'):
        return self.server.metaWeblog.getRecentPosts('', self.user, self.password, count)
    def getUserBlogs(self):
        return self.server.blogger.getUsersBlogs('', self.user, self.password)
if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'usage:', sys.argv[0], 'username password file'
        exit(0)
    blog = MetaWeblog('http://blog.chinaunix.net/xmlrpc.php?r=rpc/server', sys.argv[1], sys.argv[2])
    if os.path.isfile(sys.argv[3]):
        title,ext = os.path.splitext(os.path.split(sys.argv[3])[1])
        print title,ext
        with open(sys.argv[3], 'rb') as f:
            content = f.read()
            content = content.replace('\r', '')
            content = content.replace('\n', '<br>')
            content = content.replace(' ', '&nbsp;')
            content = content.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
            if sys.platform == 'win32':
                print blog.newPost(title, content)
            f.close()
    else:
        print sys.argv[3], 'is not exist'
