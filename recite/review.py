#encoding:utf8
import recite

if __name__ == '__main__':
    v = recite.words('review')
    while True:
        v = recite.loop(v, False)
        if len(v) == 0:
            break
