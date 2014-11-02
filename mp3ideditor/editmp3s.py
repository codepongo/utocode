import id3v2_tag_editor
import os
import sys

def main(argv):
    d = argv[0]
    if d[-1] == os.sep:
        d = d[:-1]
    d = d[(d.rfind(os.sep))+1:]
    artist, album = d.split(' - ')
    for dirpath, dirname, filenames in os.walk(argv[0]):
        for i in xrange(len(filenames)):
            if '.mp3' == os.path.splitext(filenames[i])[1]:
                inp_file = os.path.join(dirpath, filenames[i])
                print inp_file
                paramters = [];
                paramters.append('-a')
                paramters.append(str(artist))
                paramters.append('-A')
                paramters.append(str(album))
                paramters.append(inp_file)
                id3v2_tag_editor.main(paramters)
if __name__ == '__main__':
    main(sys.argv[1:])
