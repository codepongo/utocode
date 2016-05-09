import urllib
import HTMLParser
us_tbl = {
    '\xca\x8a':'U',
    '\xc9\xaa':'I',
    '\xc3\xa6':'Q',
    '\xc9\x91':'A',
    '\xc9\x9c':'E',
    '\xc9\x94':'C',
    '\xca\x8c':'V',
    '\xc9\x99':'E',
    '\xce\xb8':'T',
    '\xc5\x8b':'N',
    '\xc3\xb0':'D',
    '\xca\x83':'S',
    '\xca\x92':'Z',
    '\xc9\xa1':'g',
    '\xcb\x88':"`",
    '\xcb\x8c':',',
    '\xc9\x9b':'e',
    '\xc9\x92':'o',
    '\xcb\x90':'',

}
def phonetic_readability(s, tbl):
    for k, v in tbl.items():
        s = s.replace(k, v)
    return s

def get_from_bing(w):
    url = 'http://cn.bing.com/dict/?q=%s' % w
    class Parser(HTMLParser.HTMLParser):
        def __init__(self):
            HTMLParser.HTMLParser.__init__(self)
            self.content = ''

        def handle_starttag(self, tag, attrs):
            if tag == 'meta':
                for key, value in attrs:
                    if key == 'name' and value == 'description':
                        for k, v in attrs:
                            if k == 'content':
                                self.content = v
                                return
    rep = urllib.urlopen(url)
    html = rep.read()
    p = Parser()
    try:
        p.feed(html)
    except:
        pass
    content = p.content
    phonetic = {'en':'', 'us':'', 'us_unicode':''}
    start = content.find('[')
    end = content.find(']')
    if start == -1 or end == -1:
        return phonetic
    phonetic['us'] = phonetic_readability(content[start+1:end], us_tbl)
    start = content[end+1:].find('[')
    end = content[end+1:].find('[')
    phonetic['en'] = content[start+1:end]
    phonetic['us_unicode'] = repr(content[start+1:end])
    return phonetic


if __name__ == '__main__':
    import sys
    p = get_from_bing(sys.argv[1])
    print p





