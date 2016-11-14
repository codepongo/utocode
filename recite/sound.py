import urllib
import urllib2
import re
import os
import sys
if sys.platform == 'win32':
    import mp3play
elif sys.platform == 'darwin':
    pass
else:
    pass
import socket
sound_dir = 'sound'
def download(url, path):
    try:
        import proxy
        proxy_url = 'http://%s:%s' % (proxy.ip, proxy.port)
        proxy = urllib2.ProxyHandler({'http':proxy_url})
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)
    except ImportError, e:
        pass
    try:
        if not os.path.isfile(path):
            conn = urllib2.urlopen(url)
            with open(path, 'wb') as f:
                f.write(conn.read())
        return True
    except socket.error, e:
        if e.errno == 10054:
            return False
        raise e
def play(f):
    if os.path.getsize(f) == 0:
        return
    if sys.platform == 'darwin':
        return os.system('afplay %s' % f)
    try:
        clip = mp3play.load(f)
        clip.play()
        # Let it play for up to 30 seconds, then stop it.
        import time
        time.sleep(clip.seconds())
        clip.stop()
    except:
        pass

def sound(w):
    if w == '':
        return
    if not os.path.exists(sound_dir):
        os.mkdir(sound_dir)
    urls = [
        'http://media.shanbay.com/audio/us/%s.mp3' % (w),
        'http://media.engkoo.com:8129/en-us/%s.mp3' % (w),
    ]
    w += '.mp3'
    path = os.path.join(sound_dir, w)
    for url in urls:
        if download(url, path):
            play(path)
            return True
    return False


if __name__ == '__main__':
    import sys
    w = sys.argv[1].decode(sys.stdin.encoding).encode('gbk')
    urls = [
        'http://media.shanbay.com/audio/us/%s.mp3' % (w),
        'http://media.engkoo.com:8129/en-us/%s.mp3' % (w),
    ]
    path = w +'.mp3'
    for url in urls:
        if os.path.isfile(path):
            os.remove(path)
        if download(url, path):
            print url, '->', path 
            play(path)
            os.remove(path)
        else:
            print 'fail to download ', url
