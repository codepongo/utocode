import os
import hashlib
import getopt
import sys

def hashDir(directory):
    d = dict()
    for dirpath, dirnames, filenames in os.walk(directory):
        for i in xrange(len(filenames)):
            full_name = os.path.join(dirpath, filenames[i])
            if directory[-1] == os.sep:
                relative_path = full_name[len(directory):]
            else:
                relative_path = full_name[len(directory)+1:]
            with open(full_name) as f:
                c = f.read()
                f.close()
            m = hashlib.md5()
            m.update(c)
            md5 = str(m.hexdigest())
            d[full_name] = (relative_path, md5)
    return d

def compare(d1, d2):
    return sorted(list(set([i[0] for i in set(d1.values())^set(d2.values())])))



def usage():
    print ("""\
USAGE:
    %s [-h|--help] dir1 dir2
""") % (sys.argv[0])
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except:
        usage()
        return 0
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            return 0
    for i in compare(hashDir(args[0]), hashDir(args[1])):
        print i
if __name__ == '__main__':
    exit(main())
