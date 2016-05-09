#encoding:utf8
import os
import mp3play
import getch
import time
import sys
import sound
import datetime
import phonetic_with_bing as phonetic

def words(folder='vocabulary'):
    vocabulary = []
    for f in os.listdir(folder):
        if os.path.splitext(f)[1] != '.txt':
            continue
        with open(os.path.join(folder, f) , 'rb') as f:
            for line in f.readlines():
                word, t = line.split('\t ')
                w = {}
                w['word'] = word
                w['translation'] = t
                sep = t.find('/ ') 
                if sep != -1:
                    w['phonetic'] = '/' + t[0:sep].replace('/', '') + '/'
                    w['translation'] = t[sep+len('/ '):]
                vocabulary.append(w)
    return vocabulary
def exit():
    print 'do you want to exit? (Y)es/(n)o'
    if 'Y' == getch.getch():
        sys.exit(0)
def repeat(word):
    while True:
        sound.sound(word)
        c = getch.getch()
        if '\x1b' == c:
            exit()
        elif '3' == c:
            continue
        else:
            if 0 == ord(c): #Fun
                getch.getch()
            elif 79 == ord(c): #end
                getch.getch()
            elif 80 == ord(c): #down
                getch.getch()
            elif 81 == ord(c): #PageDown
                getch.getch()
            else:
                pass
                #print 'input:', ord(c), 
            break
    return c

def unknow():
    print'[x]',
    if '\x1b' == getch.getch():
        exit()
    print ''

def loop(v, save=True):
    count = len(v)
    times = len(v) + 1
    unknowV = []
    for w in v:
        times -= 1
        word = w['word']
        translation = w['translation']
        if not w.has_key('phonetic'):
            p = phonetic.get_from_bing(word)['us']
            w['phonetic'] = '['+ p +']'
        if save:
            with open('w.txt', 'a+') as f:
                line = '%s\t /%s/ %s' % (word, w['phonetic'][1:-1], translation)
                f.write(line.replace('\r', ''))

        print '[%d(%d)/%d]' % (times, times+len(unknowV), count),
        c = repeat(word)
        if 'l' == c:
            print ''
            print len(unknowV)
            for ww in unknowV:
                print ww['word'],
                if ww['word'] == word:
                    break
            print ''
            print '[%d(%d)/%d]' % (times, times+len(unknowV), count),
            c = repeat(word)
        print '%s ' % (w['phonetic']),
        repeat(word)
        print word,
        c = repeat(word)
        if '\x1b' == c:
            exit()
        print translation[:-2],
        if '1' == c:
            c = getch.getch()
            if '1' == c:
                print '[o]'
            else:
                unknow()
                unknowV.append(w)
            continue
        if '2' == c:
            unknow()
            unknowV.append(w)
            continue
    return unknowV 

if __name__ == '__main__':
    start = 0
    save = False
    if len(sys.argv) >= 1:
        try:
            start = int(sys.argv[1])
        except:
            start = 0
        save = True

    v = words()[start:]
    while True:
        v = loop(v, save)
        print v
        save = False
        if len(v) == 0:
            break