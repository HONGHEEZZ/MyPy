
import hashlib
'''
1. ANTI MALWARE TESTFILE --> eicar 바이러스
  .- https://www.eicar.org/?page_id=3950

2. KISA 인터넷보호나라 - 맞춤 전용 백신.
  .- https://www.boho.or.kr/download/dedicatedVaccine/download.do
'''

import sys
import os
import hashlib

VirusDB = []

g_vdb = []  # 가공된 악성코드 DB가 저장된다.
g_vsize = [] #악성코드의 파일 크기만 저장한다.

# ------------------------------------------------------------------------------
# * 악성코드 DB를 가공한다.
# ------------------------------------------------------------------------------
def MakeVirusDB():
    for pattern in VirusDB:
        t = []
        v = pattern.split(':')  # 세미콜론을 기준으로 자른다.
        t.append(v[1])  # MD5 해시를 저장한다.
        t.append(v[2])  # 악성코드 이름을 저장한다.
        g_vdb.append(t)  # 최종 vbd에 저장한다.

        size = int(v[0]) # 악성 코드의 파일크기
        if g_vsize.count(size) == 0: # 이미 해당 크기가 등록되었나?
            g_vsize.append(size)


# ------------------------------------------------------------------------------
# * 악성 코드를 검사한다.
# ------------------------------------------------------------------------------
def SearchVDB(fmd5):
    for t in g_vdb:
        if t[0] == fmd5:  # MD5 해시가 같은지 비교
            return True, t[1]  # 악성 코드 이름을 함께 리턴.


# 악성코드 패턴 로드하기
def LoadVirusDB():
    #fp = open('virus.db', 'rb')
    fp = open('virus.db', 'r')
    while True:
        line = fp.readline()
        if not line: break

        line = line.strip() #crlf remove
        VirusDB.append(line)

    fp.close()
# ------------------------------------------------------------------------------
# * main 함수...
# ------------------------------------------------------------------------------
def mainVirus():
    #악성 코드 패턴을 파일에서 읽는다.
    LoadVirusDB()

    # ------------------------------------------------------------------------------
    # 악성코드 DB를 가공한다.
    # ------------------------------------------------------------------------------
    MakeVirusDB()

    # 커맨드 라인으로 악성코드를 검사할 수 있게 한다.ㅣ
    # 커맨드라인의 입력 방식을 체크한다.
    if len(sys.argv) != 2:
        print('Usage : main.py [file]')
        exit(0)

    fname = sys.argv[1]

    size = os.path.getsize(fname)   #검사대상파일의 크기를 구한다.

    # ------------------------------------------------------------------------------
    # * 대상 파일의 size가 바이러스 db에 등록 된 경우에만 검사...
    # ------------------------------------------------------------------------------
    if g_vsize.count(size):
        print('******* 바이러스 검사 시작...')
        fp = open(fname, 'rb')
        fbuf = fp.read()
        fp.close()

        m = hashlib.md5()
        m.update(fbuf)
        fmd5 = m.hexdigest()

        ret, vname = SearchVDB(fmd5)
        if ret == True:
            print('%s : %s virus found...' % (fname, vname))
            # os.remove(fname)
        else:
            print('%s : ok' % (fname))

    print('******* main() 종료...')

