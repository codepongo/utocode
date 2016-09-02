#encoding:utf8
import os
import mp3play
import getch
import time
import sys
import sound
import datetime
import phonetic_with_bing as phonetic

def learning(unknowV):
    print ''
    print len(unknowV)
    for ww in unknowV:
        print ww['word'],
    print ''
    while True:
        i = raw_input('>')
        if i == ',quit':
            break
        elif i[0] == ',':
            for w in unknowV:
                if w['word'] == i[1:]:
                    sound.sound(i[1:])
                    print '%s\t /%s/ %s' % (w['word'], w['phonetic'][1:-1], w['translation'])
        else:
            continue
    print ''

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
    print '\ndo you want to exit? (Y)es/(n)o'
    if 'Y' == getch.getch():
        sys.exit(0)
def repeat(word):
    while True:
        sound.sound(word)
        c = getch.getch()
        if '3' == c:
            continue
        break

    return c
def reply(c):
    if '\x1b' == c:
        exit()
    elif 0 == ord(c): #Fun
        getch.getch()
    elif 79 == ord(c): #end
        getch.getch()
    elif 80 == ord(c): #down
        getch.getch()
    elif 81 == ord(c): #PageDown
        getch.getch()
    else:
        pass
    return c

def unknow():
    print'[x]',
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
        c = reply(repeat(word))
        if 'l' == c:
            learning(unknowV)
            print '[%d(%d)/%d]' % (times, times+len(unknowV), count),
            c = reply(repeat(word))
        print '%s ' % (w['phonetic']),
        c = reply(repeat(word))
        print word,
        c = reply(repeat(word))
        print translation[:-2],
        c = reply(repeat(word))
        if '1' == c:
            print '[o]'
            continue
        else:
            unknow()
            unknowV.append(w)
            continue
    if len(unknowV) == 0:
        return

    for u in unknowV:
        print u['word']
    return loop(unknowV, False)

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
    loop(v, save)
