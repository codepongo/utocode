# -*- coding: utf-8 -*-
import id3v2_tag_editor
import os
import sys

def main(argv):
    if sys.platform == 'win32':
        d = argv[0].decode('gbk').encode('utf-8')
    else:
        d = argv[0]
    if d[-1] == os.sep:
        d = d[:-1]
    d = d[(d.rfind(os.sep))+1:]
    if len(argv) == 3:
        artist, album = argv[1], argv[2]
        if sys.platform == 'win32':
            artist = artist.decode('gbk').encode('utf-8')
            album = album.decode('gbk').encode('utf-8')
    else:
        artist, album = d.split(' - ')
    for dirpath, dirname, filenames in os.walk(argv[0]):
        for i in xrange(len(filenames)):
            if '.mp3' == os.path.splitext(filenames[i])[1]:
                inp_file = os.path.join(dirpath, filenames[i])
                print inp_file
                paramters = [];
                #paramters.append('-v')
                paramters.append('-a')
                paramters.append(str(artist))
                paramters.append('-A')
                paramters.append(str(album))
                paramters.append(inp_file)
                id3v2_tag_editor.main(paramters)
if __name__ == '__main__':
    main(sys.argv[1:])
