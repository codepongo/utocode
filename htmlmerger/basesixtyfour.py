import sys
import base64

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print '''
Usage:
%s FILE
file is a filename''' % (sys.argv[0])
    sys.exit(0)
    print encode(sys.argv[1])

def encode(file):
    with open(file, 'rb') as f:
        b64 = base64.b64encode(f.read())
        f.close()
        return b64
    return None
