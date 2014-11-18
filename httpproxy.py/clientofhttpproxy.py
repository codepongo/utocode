import sys
import getopt
import urllib2
def http_with_proxy(proxy, original):
    httpHandler = urllib2.HTTPHandler(debuglevel=1)
    httpsHandler = urllib2.HTTPSHandler(debuglevel=1)
    proxy = urllib2.ProxyHandler({'http':proxy})
    opener = urllib2.build_opener(httpHandler, httpsHandler, proxy)
    urllib2.install_opener(opener)
    return urllib2.urlopen(original).read()

def usage():
    usage = '''usage:
%s <url> [-p|--proxy=http://ip:port]
''' % (sys.argv[0]) + ' ' * len(sys.argv[0]) + ' [-h|--help]'
    print usage
    sys.exit(0)
if __name__ == '__main__':
    proxy = ''
    original = ''
    opts, args = getopt.getopt(sys.argv[1:], 'p:h', ['proxy=', 'help'])
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
        if o in ('-p', '--proxy'):
            proxy = a
    if len(args) == 1:
        original = args[0]
    else:
        usage()
    if proxy == '':
        proxy = 'http://127.0.0.1:8000'

    print http_with_proxy(proxy, original)
