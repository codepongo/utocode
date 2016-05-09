import sys
import os
import shutil
def copytree_f(s, d):
    if os.path.isdir(d):
        shutil.rmtree(d)
    shutil.copytree(s, d)
if __name__ == '__main__':
    folders = ['review',
            'sound',
            'vocabulary',
    ]
    out = sys.argv[1]
    for f in folders:
        d = os.path.join(out, f)
        if not os.path.exists(d):
            os.mkdir(d)
    libs = [
            'mp3play',
    ]
    for l in libs:
        copytree_f(l, os.path.join(out, l))
    excutes = [
            'getch.py',
            'p.py',
            'phonetic_with_bing.py',
            'recite.py',
            'sound.py',
            'review.py',
            'p.bat',
            'r.bat',
            'review.bat',
            's.bat',
    ]
    for e in excutes:
        shutil.copy(e, out)

    if os.path.isfile('install.py'):
        with open('install.py', 'rb') as f:
            with open(os.path.join(out, 'backup.py'), 'wb') as o:
                o.write(f.read().replace('out = sys.argv[1]', 'out = "%s"' % (os.path.abspath('.').replace('\\', '\\\\'))))

