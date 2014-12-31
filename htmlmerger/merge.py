#coding:utf8
import HTMLParser
import basesixtyfour
import re
import os
import sys

def allfilesin1(template, out):
    print template, '>', out
    with open(template, 'rb') as i:
        html = i.read()
    try:
        html = html.decode('utf8')
    except:
        pass
    with open(out, 'wb') as index:
        index.write(allin1(html))

def allin1(html):
    class Parser(HTMLParser.HTMLParser):
        def __init__(self):
            self.icons = {}
            HTMLParser.HTMLParser.__init__(self)
        def handle_starttag(self, tag, attrs):
            if tag == 'img':
                    for k, v in attrs:
                        if k == 'src':
                            file_path = v
                            self.icons[v] = basesixtyfour.encode(file_path)
    p = Parser()
    p.feed(html)
    for key, value in p.icons.iteritems():
        html = html.replace('src="'+key+'"', 'src="data:image/x-'+os.path.splitext(key)[1][1:]+';base64,' +value+'"')
    return html

if __name__ == '__main__':
    allfilesin1(sys.argv[1], sys.argv[2])
