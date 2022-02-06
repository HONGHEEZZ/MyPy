import sys
import zlib
import hashlib
import os

#주어진 파일을 암호화 한다.
def main():
    if len(sys.argv) != 2:
        print('Usage: kmake.py [file]')

    fname = sys.argv[1]
    tname = fname

    fp = open(tname, 'rb')
    buf = fp.read()


    fp.close()

    buf2 = zlib.compress(buf)

    buf3 = ''
    for c in buf2: #0xFF XOR
        #buf3 += chr(ord(c) ^ 0xFF)
        buf3 += chr(c ^ 0xFF)

    buf4 = 'KAVM' + buf3 # make header.

    f = buf4

    #hashlib.sha256(string.encode('utf-8')).hexdigest()
    #f = f.encode('utf-8')
    for i in range(3)   : #지금까지의 내용을 md5로 구한다.
        md5 = hashlib.md5()
        md5.update(f)
        f=md5.hexdigest()

    buf4+= f #md5를 암호화된 내용 뒤에 추가한다.

    kmd_name = fname.split('.')[0] + '.kmd'
    fp = open(kmd_name, 'wb')
    fp.write(buf4)
    fp.close()

    print(f'{fname} -> {kmd_name}')

if __name__ == '__main__':
    main()