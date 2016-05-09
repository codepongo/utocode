import sound
import sys
w = sys.argv[1].decode(sys.stdin.encoding).encode('gbk')
sound.sound(w)
