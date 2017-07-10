import urllib
import os
import datetime
import HTMLParser
book = 'zuohaitao.com_word'
def fetch():
    if not os.path.exists(book):
        os.mkdir(book)
    vocabulary = os.path.join(book, 'vocabulary')
    if not os.path.exists(vocabulary):
        os.mkdir(vocabulary)
    vocabulary_txt = os.path.join(vocabulary, str(datetime.date.today())) + '.txt'
    if os.path.isfile(vocabulary_txt):
        return book
    sound = os.path.join(book, 'sound')
    if not os.path.exists(sound):
        os.mkdir(sound)
    url = 'http://zuohaitao.com/word.html'
    word_html = os.path.join(book, str(datetime.date.today())) + '.html'
    response = ''
    if not os.path.isfile(word_html):
        response = urllib.urlopen(url).read()
        with open(word_html, 'wb') as f:
            f.write(response);
    else:
        with open(word_html, 'rb') as f:
            response = f.read()
    class Parser(HTMLParser.HTMLParser):
        def __init__(self):
            HTMLParser.HTMLParser.__init__(self)
            self.flag = False
            self.data = ''
        def handle_starttag(self, tag, attrs):
            if tag == 'pre':
                for key, value in attrs:
                    if key == 'style' and value.find('display:none') != -1:
                        self.flag = True
                        break
        def handle_endtag(self, tag):
                self.flag = False
        def handle_data(self, data):
            if self.flag:
                self.data += data
    p = Parser()
    p.feed(response)
    with open(vocabulary_txt, 'wb') as f:
        f.write(p.data.replace(' /', '\t /'))
    return book
