import sys
import md5
import os
import sys, time 
import urllib
import urllib2
dnstart = None
def download(url, file, reporter): 
    """download file using urllib.urlretrieve 
    support http, ftp. 
    func is callback function indicating the 
    progression""" 
    global dnstart 
    dnstart = time.time() 
    try:
        urllib.urlretrieve(url, file, reporter) 
    except IOError:
        print '%s can not be connected.' % url 
    print >> sys.stderr, '\r', 

def disp_progress(num_of_block, block_size, total): 
    """display progression in terminal""" 
    now = time.time() 
    elapsed = now - dnstart 
    bytes = num_of_block * block_size 
    v = float(bytes) / elapsed 
#   print >> sys.stderr, 'download speed is %.2f bytes/sec' % v,  
    if total != -1: 
        p = int(bytes * 10.00 / total) 
        print >> sys.stderr, '|' + '=' * p + '>'+ ' ' * (10-p) + '|', 
        print >> sys.stderr, '\r', 

if __name__ == '__main__':
    url = sys.argv[1]
    headers = urllib2.urlopen(urllib2.Request(url)).headers
    size = int(headers['content-length'])
    name = md5.new(url).hexdigest().upper()
    if os.path.exists(name) and size == os.path.getsize(name):
       print 'file is exist!'
       sys.exit(0)
    download(url, name, disp_progress)
    print 'file %s is saved.' % name
