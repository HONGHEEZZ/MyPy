from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic

import os

from socket import *
import time
import struct
import random

import ipaddress #for scan...
from subprocess import *  # for ping...
from datetime import datetime
import queue
import threading
ports = [22, 53, 80, 443, 3389] #SSH, DNS, HTTP, HTTPS, RDP

# 큐 자료를 사용해 작업 대기열을 생성
q = queue.Queue()


'''
* 파이썬 ui 참고 자료 - wikidoc
- PyQt5 Tutorial - 파이썬으로 만드는 나만의 GUI 프로그램
- 초보자를 위한 Python GUI 프로그래밍 - PyQt5
- python_ Cheat Sheet
'''

# 책 https://wikidocs.net/book/1
# 책 - 챕터 https://wikidocs.net/2



def error_checksum(msg):
    s = 0
    for i in range(0, len(msg), 2):
        w = msg[i] + (msg[i + 1] << 8)
        s = s + w
    s = (s >> 16) + (s & 0xffff)
    s = s + (s >> 6)
    s = ~s & 0xfff
    return s


def icmp():
    type = 8
    code = 0
    chksum = 0
    id = random.randint(0, 0xFFFF)
    seq = 1
    real_chksum = error_checksum(struct.pack('!BBHHH', type, code, chksum, id, seq))
    icmp_pkt = struct.pack('!BBHHH', type, code, htons(real_chksum), id, seq)
    return icmp_pkt



class CPAYLOAD:
    def __init__(self, protocol, data):
        self.type = protocol
        self.data = data

    def get_info(self):
        info = ''

        info = info + f"{'-' * 80}\n"

        info = info + f"* {self.type} Payload\n"
        info = info + f"{'-' * 80}\n"
        info = info + f"* Payload Data : {str(self.data)}\n"

        info = info + "\n"

        return info

class CIP_HEADER:
    def __init__(self):
        self.version_ip_header_length = ''
        self.version = ''
        self.ip_header_length = ''
        self.ip_header_length = ''
        self.ttl = ''
        self.protocol = ''
        self.ip_source_address = ''
        self.ip_destination_address = ''

    def set_ip_header(self, str_ip_header):
        ip_header = struct.unpack("!BBHHHBBH4s4s", str_ip_header)

        self.version_ip_header_length = ip_header[0]
        self.version = self.version_ip_header_length >> 4
        self.ip_header_length = self.version_ip_header_length & 0xF
        self.ip_header_length = self.ip_header_length * 4
        self.ttl = ip_header[5]
        self.protocol = ip_header[6]
        self.ip_source_address = inet_ntoa(ip_header[8])
        self.ip_destination_address = inet_ntoa(ip_header[9])


    def get_info(self):
        info = ''

        info = info + f"* Version : {str(self.version)}\n"
        info = info + f"* IP Header Length : {str(self.ip_header_length)}\n"
        info = info + f"* TTL: {str(self.ttl)}\n"
        info = info + f"* Protocol: {str(self.protocol)}\n"
        info = info + f"* Source IP Address :  {str(self.ip_source_address)}\n"
        info = info + f"* Destination IP Address : {str(self.ip_destination_address)}\n"
        return info


class CICMP_HEADER:
    def __init__(self):
        self.type = ''
        self.code = ''
        self.checksum = ''
        self.id = ''
        self.seq = ''

    def set_icmp_header(self, str_icmp_header):
        icmp_header = struct.unpack("!BBHHH", str_icmp_header)

        self.type = icmp_header[0]
        self.code = icmp_header[1]
        self.checksum = icmp_header[2]
        self.id = icmp_header[3]
        self.seq = icmp_header[4]


    def get_info(self):
        info = ''

        info = info + f"* Type : {str(self.type)}\n"
        info = info + f"* Code : {str(self.code)}\n"
        info = info + f"* Checksum: {str(self.checksum)}\n"
        info = info + f"* ID: {str(self.id)}\n"
        info = info + f"* Sequence :  {str(self.seq)}\n"

        return info



class CTCP_HEADER:
    def __init__(self):
        self.source_port            = ''
        self.destination_port       = ''
        self.sequence_number        = ''
        self.acknowledgment_number  = ''
        self.offset_reserved        = ''
        self.tcp_header_length      = ''
        self.window                 = ''
        self.checksum               = ''
        self.urgent_pointer         = ''

    def set_tcp_header(self, str_tcp_header):
        tcp_header = struct.unpack("!HHLLBBHHH", str_tcp_header)

        self.source_port = tcp_header[0]
        self.destination_port = tcp_header[1]
        self.sequence_number = tcp_header[2]
        self.acknowledgment_number = tcp_header[3]
        self.offset_reserved = tcp_header[4]
        self.tcp_header_length = self.offset_reserved >> 4
        self.window = tcp_header[5]
        self.checksum = tcp_header[6]
        self.urgent_pointer = tcp_header[7]

    def get_info(self):
        info = ''
        info = info + f"* Source Port Number : {str(self.source_port)}\n"
        info = info + f"* Destination Port Number : {str(self.destination_port)}\n"
        info = info + f"* Sequence Number : {str(self.sequence_number)}\n"
        info = info + f"* Acknowledgment : {str(self.acknowledgment_number)}\n"
        info = info + f"* TCP Header Length : {str(self.tcp_header_length)}\n"
        info = info + f"* Window : {str(self.window)}\n"
        info = info + f"* Checksum : {str(self.checksum)}\n"
        info = info + f"* Urgent Pointer : {str(self.urgent_pointer)}\n"
        return info


class CUDP_HEADER:
    def __init__(self):
        self.source_port = ''
        self.destination_port = ''
        self.length = ''
        self.checksum = ''

    def set_udp_header(self, str_udp_header):
        udp_header = struct.unpack("!HHHH", str_udp_header)

        self.source_port = udp_header[0]
        self.destination_port = udp_header[1]
        self.length = udp_header[2]
        self.checksum = udp_header[3]

    def get_info(self):
        info = ''

        info = info + f"* source_port : {str(self.source_port)}\n"
        info = info + f"* destination_port : {str(self.destination_port)}\n"
        info = info + f"* length: {str(self.length)}\n"
        info = info + f"* checksum: {str(self.checksum)}\n"

        return info



my_dlg = uic.loadUiType("../ui/MyHeader.ui")[0]
class CMyHeader(QDialog, my_dlg):
    def __init__(self, parent=None):
        print("parent:", parent)
        super().__init__(parent)
        self.setupUi(self)
        # loadUi("test2",self)

        self.initUI()


    # 2021.03.19 현재 소멸자 호출 안됨...
    def __del__(self):
        for i in range(0, self.cboImage.count()):
            if self.dialog[i]:
                self.dialog[i].close()



    def initUI(self):
        self.setWindowTitle('MyHeader')
        self.setMinimumSize(200, 200)

        self.btnViewImage.clicked.connect(self.btnViewImage_Click)
        self.btnViewList.clicked.connect(self.btnViewList_Click)
        self.btnPortScan.clicked.connect(self.btnPortScan_Click)

        self.btnUdpClient.clicked.connect(self.btnUdpClient_Click)
        self.btnTcpClient.clicked.connect(self.btnTcpClient_Click)
        self.btnSniffing.clicked.connect(self.btnSniffing_Click)

        #ping
        self.btnSendPing.clicked.connect(self.btnSendPing_Click)

        #스캔
        self.btnScan.clicked.connect(self.btnScan_Click)


        self.dialog = [None] * self.cboImage.count()



        self.cboContents.clear()
        self.cboContents.addItem("01.프로토콜/포트보기")
        self.cboContents.addItem("02.struct 모듈의 서식 문자열")
        self.cboContents.addItem("03.host <--> network 변환")

        # 항상 맨 마지막을 선택으로 한다.
        self.cboContents.setCurrentIndex(self.cboContents.count() - 1)

    def btnViewImage_Click(self):
        root = QFileInfo(__file__).absolutePath()
        file_name = self.cboImage.currentText()
        full_file_name = root + '/../img/packet/' + file_name
        full_file_name = os.path.normpath(full_file_name)

        curr_index = self.cboImage.currentIndex()

        self.dialog[curr_index] = QDialog()
        self.loadImageFromFile(self.dialog[curr_index], full_file_name)


    def f_packet_init(self, host):
        # 아래 값들은 소켓을 생성할 때 프로토콜을 지정하는 세 번째 인자로 사용
        # 윈도우는 프로토콜에 관계없이 들어오는 모든 패킷을 가로채기 때문에 IP를 지정해도 무관하지만 유닉스나 리눅스는 ICMP를 가로채겠다는 것을 명시적으로 표시해야함
        if os.name == 'nt':
            socket_protocol = IPPROTO_IP
            #socket_protocol = IPPROTO_UDP
        else:
            socket_protocol = IPPROTO_ICMP
        # socket_protocol로 지정된 프로토콜을 이용하는 Raw 소켓을 만들고 호스트와 바인드
        sock = socket(AF_INET, SOCK_RAW, socket_protocol)
        sock.bind((host, 0))
        # 가로채는 패킷에 IP 헤더를 포함하라고 소켓의 옵션으로 지정
        sock.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)

        # 윈도우인 경우 소켓을 promiscuous모드로 변경하여 호스트에 전달되는 모든 패킷을 수신.
        # 소켓이 promiscuous 모드가 아니면 코드가 구동되는 컴퓨터가 목적지가 아닌 패킷은 모두 버리게 됨
        if os.name == 'nt':
            sock.ioctl(SIO_RCVALL, RCVALL_ON)

        # if os.name == 'nt':
        #     sock.ioctl(SIO_RCVALL, RCVALL_OFF)

        return sock


    def f_packetSniffing(self, host):

        sock = self.f_packet_init(host)
        # 소켓으로 패킷이 들어올 때까지 대기. 65565는 버퍼의 크기로 단위는 바이트
        data = sock.recv(65565)

        print(data)

        #------------------------------------------------------------------------------
        #* IP header
        #------------------------------------------------------------------------------
        ip_header = data[0:20]

        cip_header = CIP_HEADER()
        cip_header.set_ip_header(ip_header)

        self.txtContents.append("-" * 80)
        self.txtContents.append("* IP HEADER")
        self.txtContents.append("-" * 80)
        self.txtContents.append(cip_header.get_info())

        if cip_header.protocol == 1:  # icmp
            print('****************** ICMP ************')
            # ------------------------------------------------------------------------------
            # * ICMP header
            # ------------------------------------------------------------------------------
            icmp_header = data[cip_header.ip_header_length:cip_header.ip_header_length + 8]

            cicmp_header = CICMP_HEADER()
            cicmp_header.set_icmp_header(icmp_header)

            self.txtContents.append("-" * 80)
            self.txtContents.append("* ICMP HEADER")
            self.txtContents.append("-" * 80)
            self.txtContents.append(cicmp_header.get_info())

            # ------------------------------------------------------------------------------
            # * ICMP Payload (탑재화물)
            # ------------------------------------------------------------------------------
            icmp_header_length = 8
            header_size = cip_header.ip_header_length + icmp_header_length
            payload_data_size = len(data) - header_size
            icmp_payload_data = data[header_size:]


            cpayload = CPAYLOAD("ICMP", icmp_payload_data)
            str = cpayload.get_info()
            self.txtContents.append(str)



        elif cip_header.protocol == 6: #tcp
            # ------------------------------------------------------------------------------
            # * TCP header
            # ------------------------------------------------------------------------------
            tcp_header = data[cip_header.ip_header_length:cip_header.ip_header_length+20]
            ctcp_header = CTCP_HEADER()
            ctcp_header.set_tcp_header(tcp_header)

            self.txtContents.append("-" * 80)
            self.txtContents.append("* TCP HEADER")
            self.txtContents.append("-" * 80)
            self.txtContents.append(ctcp_header.get_info())

            # ------------------------------------------------------------------------------
            # * TCP Payload (탑재화물)
            # ------------------------------------------------------------------------------
            header_size = cip_header.ip_header_length + ( ctcp_header.tcp_header_length * 4)
            payload_data_size = len(data) - header_size
            tcp_payload_data = data[header_size:]

            cpayload = CPAYLOAD("TCP", tcp_payload_data)
            self.txtContents.append(cpayload.get_info())


        elif cip_header.protocol == 17: #udp
            # ------------------------------------------------------------------------------
            # * TCP header
            # ------------------------------------------------------------------------------
            udp_header = data[cip_header.ip_header_length:cip_header.ip_header_length + 8]
            
            cudp_header = CUDP_HEADER()
            cudp_header.set_udp_header(udp_header)

            self.txtContents.append("-" * 80)
            self.txtContents.append("* UDP HEADER")
            self.txtContents.append("-" * 80)
            self.txtContents.append(cudp_header.get_info())

            # ------------------------------------------------------------------------------
            # * UDP Payload (탑재화물)
            # ------------------------------------------------------------------------------
            udp_header_length = 8
            header_size = cip_header.ip_header_length + udp_header_length
            payload_data_size = len(data) - header_size
            udp_payload_data = data[header_size:]

            cpayload = CPAYLOAD("TCP", udp_payload_data)
            str = cpayload.get_info()
            self.txtContents.append(str)


        self.txtContents.ensureCursorVisible()
        self.txtContents.repaint()

        print("")
        zz = 0


    def btnSniffing_Click(self, ip):

        print(gethostname())
        host = gethostbyname(gethostname())
        print('start sniffing {0}'.format(host))
        self.f_packetSniffing('192.168.0.10')  # 호스트 이름을 IPv4형식으로 변경한 ip를 했을 때 에러나서 임시 ip 지정

    def btnSendPing_Click(self, ip):

        s = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)

        while True:
            s.sendto(icmp(), ('192.168.0.1', 0))
            self.txtContents.append("ping to 192.168.0.1")
            self.txtContents.ensureCursorVisible()
            self.txtContents.repaint()
            time.sleep(1)

    def btnScan_Click(self):
        self.f_scanMain()


    def f_scanMain(self):

        self.txtContents.clear()

        # 시작시간
        start_time = datetime.now()

        #스레드를 30개 생성
        threads = []
        for i in range(20):
            #각 쓰레드가 함수를 수행하도록 설정
            t = threading.Thread(target = self.f_scan_worker)

            #쓰레드가 백그라운드에서 실행되도록 데몬으로 지정
            t.setDaemon(True)

            #해당 쓰레드 작업을 실시
            t.start()

            #쓰레드 관리 목록에 저장
            threads.append(t)

        ip_range = list(ipaddress.ip_network("192.168.0.0/24"))
        for host in ip_range[1:-245]:  # 범위내의 모든 ip에 검사 실시
            q.put(host)

        #대기열에 추가되어 있는 모든 작업들이 모두 완료될때까지 대기
        q.join()

        #쓰레드 종료 처리
        for i in range(20):
            q.put(None) #대기열에 빈 작업을 할당해 처리
        for t in threads:
            t.join()

        end_time = datetime.now()

        # 종료 메시지와 수행시간 표시
        msg = str(end_time - start_time)
        self.txtContents.append(f"Sacnning completed in : {msg}")


        print('******************* Killed.... *****************')

    def f_scan_worker(self):
        while True:  # 무한 루프로 작업 대기열의 모든 작업 반복 처리
            # 작업 대기열에서 호스트 IP를 하나씩 가져옴
            target = q.get()

            # 유효하지 않은 호스트인 경우 루프탈출 후 쓰레드 종료
            if target is None:
                break

            self.f_scanner(target)

            # 해당 호스트에 대한 스캔 작업을 완료했다는 task_done 신호
            q.task_done()

    def f_scanner(self, host):

        if os.name == 'nt':
            alive = os.system(f"ping -n 1 {host}")
            # pipe = Popen(f"ping -n 1 {host}", shell = True, stdout = PIPE) # 표준 출력을 파이프로 보낸다.
            # print(pipe.stdout.read().decode('mbcs'))
        else:
            alive = os.system(f"ping -c 1 {host}")

        if alive != 0:  # ping 명령에 대한 응답이 성곻하면 0이 반환됨
            # 작업 시간 및 로그 기록
            timelog = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.txtContents.append(f"{timelog} : taget host {host} is down...")
            #print(f"{timelog} : taget host {host} is down...")

        elif alive == 0:  # ping 명령에 대한 응답이 성곻하면 0이 반환됨
            #작업 시간 및 로그 기록
            timelog = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.txtContents.append(f"{timelog} : taget host {host} is up...")
            print(f"{timelog} : taget host {host} is up...")

            #포트 스캔 실시
            for port in ports:  #포트
                #소켓 생성
                sock = socket(AF_INET, SOCK_STREAM)
                sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

                self.txtContents.append(f"* before connect_ex {str(host)} {str(port)}")
                print(f"* before connect_ex {str(host)} {str(port)}")
                result = sock.connect_ex((str(host), port))
                self.txtContents.append(f"* after connect_ex {str(host)} {str(port)}")
                print(f"* after connect_ex {str(host)} {str(port)}")

                if result == 0:
                    self.txtContents.append(f"-------> Port {str(host)} : {str(port)} is opened....")

                    print(f"-------> Port {str(host)} : {str(port)} is opened....")
                    time.sleep(0.01)
                else:
                    self.txtContents.append(f"-------> {str(host)} : {str(port)} is closed...")
                    print(f"-------> Port {str(host)} : {str(port)} is closed...")
                sock.close()

                self.txtContents.ensureCursorVisible()
                self.txtContents.repaint()



    def f_tcpClient(self, ip, port, message, raw = False):
        sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        sock.connect((ip, port))
        ret = sock.sendto(message, (ip, port))
        time.sleep(1)
        sock.close()

    def btnTcpClient_Click(self):
        self.txtContents.append("**** Start tcp send ****")
        self.f_tcpClient('127.0.0.1', 3000, b"good moring_123456789x", True)
        self.txtContents.append("**** End tcp send ****")



    def f_udpClient(self, ip, port, message, raw = False):

        if raw == False:
            sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
            sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

            ret = sock.sendto(message, (ip, port))


        elif raw == True:
            # 사용자가 8바이트 크기의 UDP 헤더를 직접 구현하겠다는 의미
            sock = socket(AF_INET, SOCK_RAW, IPPROTO_UDP)

            #IP 헤더 로우소켓 실패....
            #sock.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)

            source_port = 4321
            destination_port = 3000
            length = 8 + len(message)
            checksum = 0
            udp_header = struct.pack('!HHHH', source_port, destination_port, length, checksum)

            udp_packet = udp_header + message


            sock.sendto(udp_packet, (ip, port))




    def btnUdpClient_Click(self):
        self.txtContents.append("**** Start udp send ****")
        self.f_udpClient('127.0.0.1', 3000, b"good moring_123456789x", True)
        self.txtContents.append("**** End udp send ****")

    def btnPortScan_Click(self):

        self.txtContents.clear()
        self.txtContents.append("**** Start Port Scan ****")

        hosts = ['192.168.0.10']
        #hosts = ['127.0.0.1']
        for host in hosts:
            for port in range(1518, 1525):
                s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
                s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

                try:

                    result = s.connect_ex((host, port))

                    if result == 0:
                        self.txtContents.append(f"{host} [*]Port [{port}] opened***")
                    else:
                        self.txtContents.append(f"{host} [*]Port [{port}] closed")
                    self.txtContents.repaint()
                    time.sleep(0.001)
                except:
                    pass

        self.txtContents.append("**** End Port Scan ****")

    def btnViewList_Click(self):
        curText = self.cboContents.currentText()

        if curText == '01.프로토콜/포트보기':
            self.listupProtocolPort(self.txtContents)
        elif curText == '02.struct 모듈의 서식 문자열':
            self.listupStrucFormatString(self.txtContents)
        elif curText == '03.host <--> network 변환':
            self._03(self.txtContents)

    def myTitleComment(self, txtContents, title):
        txtContents.append("")
        txtContents.append("-" * 80)
        txtContents.append(f"-* {title}")
        txtContents.append("-" * 80)

    def _03(self, txtContents):
        self.txtContents.clear()
        txtContents.append('* pack() : 10진수를 16진수로 변경')
        txtContents.append('* unpack() : 16진수를 10진수로 변경')
        txtContents.append('* inet_aton() : 문자열을 빅 엔디안 방식으로 변경')
        txtContents.append('* inet_ntoa() : 빅엔디안 방식을 문자열로 변경')
        txtContents.append('* htons() : 호스트 바이트 순서방식을 네트워크 바이스 툰서 방식으로 변경')
        txtContents.append('* ntohs() : 네트워크 바이트 순서방식을 호스트 바이스 툰서 방식으로 변경')

        txtContents.append('')
        txtContents.append('>>> import socket, struct')
        txtContents.append('>>> k = struct.unpack("!i", inet_aton("127.0.0.1")')
        txtContents.append('>>> print(k)')
        txtContents.append('>>> 2130706433')

        txtContents.append('')
        txtContents.append('* 프로토콜 헤더별 대응 형식 문자열')
        txtContents.append('* UDP : \t!HHHH')
        txtContents.append('* 가상 : \t!4s4sBBH')
        txtContents.append('* TCP : \t!HHLLBBHHH')
        txtContents.append('* IP : \t!BBHHHBBH4s4s')
        txtContents.append('* ICMP : \t!BBHHH')
        txtContents.append('* ARP : \t!2s2s1s1s2s6s4s6s4s')
        txtContents.append('* Ethernet: \t!6s6s2s')




    def listupStrucFormatString(self, txtContents):
        mytxt = '''<h3>struct 모듈의 서식 문자열 </h3>
        https://python.flowdas.com/library/struct.html
                <table class="docutils align-default">
        <colgroup>
        <col style="width: 10%">
        <col style="width: 32%">
        <col style="width: 24%">
        <col style="width: 20%">
        <col style="width: 15%">
        </colgroup>
        <thead>
        <tr class="row-odd"><th class="head"><p>포맷</p></th>
        <th class="head"><p>C형</p></th>
        <th class="head"><p>파이썬 형</p></th>
        <th class="head"><p>표준 크기</p></th>
        <th class="head"><p>노트</p></th>
        </tr>
        </thead>
        <tbody>
        <tr class="row-even"><td><p><code class="docutils literal notranslate"><span class="pre">x</span></code></p></td>
        <td><p>패드 바이트</p></td>
        <td><p>값이 없습니다</p></td>
        <td></td>
        <td></td>
        </tr>
        <tr class="row-odd"><td><p><code class="docutils literal notranslate"><span class="pre">c</span></code></p></td>
        <td><p><code class="xref c c-type docutils literal notranslate"><span class="pre">char</span></code></p></td>
        <td><p>길이가 1인 bytes</p></td>
        <td><p>1</p></td>
        <td></td>
        </tr>
        <tr class="row-even"><td><p><code class="docutils literal notranslate"><span class="pre">b</span></code></p></td>
        <td><p><code class="xref c c-type docutils literal notranslate"><span class="pre">signed</span> <span class="pre">char</span></code></p></td>
        <td><p>정수</p></td>
        <td><p>1</p></td>
        <td><p>(1), (2)</p></td>
        </tr>
        <tr class="row-odd"><td><p><code class="docutils literal notranslate"><span class="pre">B</span></code></p></td>
        <td><p><code class="xref c c-type docutils literal notranslate"><span class="pre">unsigned</span> <span class="pre">char</span></code></p></td>
        <td><p>정수</p></td>
        <td><p>1</p></td>
        <td><p>(2)</p></td>
        </tr>
        <tr class="row-even"><td><p><code class="docutils literal notranslate"><span class="pre">?</span></code></p></td>
        <td><p><code class="xref c c-type docutils literal notranslate"><span class="pre">_Bool</span></code></p></td>
        <td><p>bool</p></td>
        <td><p>1</p></td>
        <td><p>(1)</p></td>
        </tr>
        <tr class="row-odd"><td><p><code class="docutils literal notranslate"><span class="pre">h</span></code></p></td>
        <td><p><code class="xref c c-type docutils literal notranslate"><span class="pre">short</span></code></p></td>
        <td><p>정수</p></td>
        <td><p>2</p></td>
        <td><p>(2)</p></td>
        </tr>
        <tr class="row-even"><td><p><code class="docutils literal notranslate"><span class="pre">H</span></code></p></td>
        <td><p><code class="xref c c-type docutils literal notranslate"><span class="pre">unsigned</span> <span class="pre">short</span></code></p></td>
        <td><p>정수</p></td>
        <td><p>2</p></td>
        <td><p>(2)</p></td>
        </tr>
        <tr class="row-odd"><td><p><code class="docutils literal notranslate"><span class="pre">i</span></code></p></td>
        <td><p><code class="xref c c-type docutils literal notranslate"><span class="pre">int</span></code></p></td>
        <td><p>정수</p></td>
        <td><p>4</p></td>
        <td><p>(2)</p></td>
        </tr>
        <tr class="row-even"><td><p><code class="docutils literal notranslate"><span class="pre">I</span></code></p></td>
        <td><p><code class="xref c c-type docutils literal notranslate"><span class="pre">unsigned</span> <span class="pre">int</span></code></p></td>
        <td><p>정수</p></td>
        <td><p>4</p></td>
        <td><p>(2)</p></td>
        </tr>
        <tr class="row-odd"><td><p><code class="docutils literal notranslate"><span class="pre">l</span></code></p></td>
        <td><p><code class="xref c c-type docutils literal notranslate"><span class="pre">long</span></code></p></td>
        <td><p>정수</p></td>
        <td><p>4</p></td>
        <td><p>(2)</p></td>
        </tr>
        <tr class="row-even"><td><p><code class="docutils literal notranslate"><span class="pre">L</span></code></p></td>
        <td><p><code class="xref c c-type docutils literal notranslate"><span class="pre">unsigned</span> <span class="pre">long</span></code></p></td>
        <td><p>정수</p></td>
        <td><p>4</p></td>
        <td><p>(2)</p></td>
        </tr>
        <tr class="row-odd"><td><p><code class="docutils literal notranslate"><span class="pre">q</span></code></p></td>
        <td><p><code class="xref c c-type docutils literal notranslate"><span class="pre">long</span> <span class="pre">long</span></code></p></td>
        <td><p>정수</p></td>
        <td><p>8</p></td>
        <td><p>(2)</p></td>
        </tr>
        <tr class="row-even"><td><p><code class="docutils literal notranslate"><span class="pre">Q</span></code></p></td>
        <td><p><code class="xref c c-type docutils literal notranslate"><span class="pre">unsigned</span> <span class="pre">long</span>
        <span class="pre">long</span></code></p></td>
        <td><p>정수</p></td>
        <td><p>8</p></td>
        <td><p>(2)</p></td>
        </tr>
        <tr class="row-odd"><td><p><code class="docutils literal notranslate"><span class="pre">n</span></code></p></td>
        <td><p><code class="xref c c-type docutils literal notranslate"><span class="pre">ssize_t</span></code></p></td>
        <td><p>정수</p></td>
        <td></td>
        <td><p>(3)</p></td>
        </tr>
        <tr class="row-even"><td><p><code class="docutils literal notranslate"><span class="pre">N</span></code></p></td>
        <td><p><code class="xref c c-type docutils literal notranslate"><span class="pre">size_t</span></code></p></td>
        <td><p>정수</p></td>
        <td></td>
        <td><p>(3)</p></td>
        </tr>
        <tr class="row-odd"><td><p><code class="docutils literal notranslate"><span class="pre">e</span></code></p></td>
        <td><p>(6)</p></td>
        <td><p>float</p></td>
        <td><p>2</p></td>
        <td><p>(4)</p></td>
        </tr>
        <tr class="row-even"><td><p><code class="docutils literal notranslate"><span class="pre">f</span></code></p></td>
        <td><p><code class="xref c c-type docutils literal notranslate"><span class="pre">float</span></code></p></td>
        <td><p>float</p></td>
        <td><p>4</p></td>
        <td><p>(4)</p></td>
        </tr>
        <tr class="row-odd"><td><p><code class="docutils literal notranslate"><span class="pre">d</span></code></p></td>
        <td><p><code class="xref c c-type docutils literal notranslate"><span class="pre">double</span></code></p></td>
        <td><p>float</p></td>
        <td><p>8</p></td>
        <td><p>(4)</p></td>
        </tr>
        <tr class="row-even"><td><p><code class="docutils literal notranslate"><span class="pre">s</span></code></p></td>
        <td><p><code class="xref c c-type docutils literal notranslate"><span class="pre">char[]</span></code></p></td>
        <td><p>bytes</p></td>
        <td></td>
        <td></td>
        </tr>
        <tr class="row-odd"><td><p><code class="docutils literal notranslate"><span class="pre">p</span></code></p></td>
        <td><p><code class="xref c c-type docutils literal notranslate"><span class="pre">char[]</span></code></p></td>
        <td><p>bytes</p></td>
        <td></td>
        <td></td>
        </tr>
        <tr class="row-even"><td><p><code class="docutils literal notranslate"><span class="pre">P</span></code></p></td>
        <td><p><code class="xref c c-type docutils literal notranslate"><span class="pre">void</span> <span class="pre">*</span></code></p></td>
        <td><p>정수</p></td>
        <td></td>
        <td><p>(5)</p></td>
        </tr>
        </tbody>
        </table>
        
        <h3>바이트 순서 제어문자</h3>
        <table class="docutils align-default">
<colgroup>
<col style="width: 20%">
<col style="width: 43%">
<col style="width: 18%">
<col style="width: 20%">
</colgroup>
<thead>
<tr class="row-odd"><th class="head"><p>문자</p></th>
<th class="head"><p>바이트 순서</p></th>
<th class="head"><p>크기</p></th>
<th class="head"><p>정렬</p></th>
</tr>
</thead>
<tbody>
<tr class="row-even"><td><p><code class="docutils literal notranslate"><span class="pre">@</span></code></p></td>
<td><p>네이티브</p></td>
<td><p>네이티브</p></td>
<td><p>네이티브</p></td>
</tr>
<tr class="row-odd"><td><p><code class="docutils literal notranslate"><span class="pre">=</span></code></p></td>
<td><p>네이티브</p></td>
<td><p>표준</p></td>
<td><p>none</p></td>
</tr>
<tr class="row-even"><td><p><code class="docutils literal notranslate"><span class="pre">&lt;</span></code></p></td>
<td><p>리틀 엔디안</p></td>
<td><p>표준</p></td>
<td><p>none</p></td>
</tr>
<tr class="row-odd"><td><p><code class="docutils literal notranslate"><span class="pre">&gt;</span></code></p></td>
<td><p>빅 엔디안</p></td>
<td><p>표준</p></td>
<td><p>none</p></td>
</tr>
<tr class="row-even"><td><p><code class="docutils literal notranslate"><span class="pre">!</span></code></p></td>
<td><p>네트워크 (= 빅 엔디안)</p></td>
<td><p>표준</p></td>
<td><p>none</p></td>
</tr>
</tbody>
</table>

'''
        txtContents.setHtml(mytxt)

        mytxt =r'''
from struct import *
pack('>hhl', 1, 2, 3) #빅엔디안 short short long
Out[12]: b'\x00\x01\x00\x02\x00\x00\x00\x03'

pack('<hhl', 1, 2, 3) #리틀엔디안
Out[13]: b'\x01\x00\x02\x00\x03\x00\x00\x00'
        '''
        txtContents.append(mytxt)

    def listupProtocolPort(self, txtContents):
        #------------------------------------------------------------------------------
        # /etc/services 파일에서 동일 이름을 찾아서 리턴함.
        #------------------------------------------------------------------------------
        self.myTitleComment(txtContents, 'TCP')
        protocols = ["ftp", "ssh", "telnet", "smtp", "http", "pop3"]
        for protocol in protocols:
            strServiceName = getservbyname(protocol, "tcp")
            cont = f"* The port number for {protocol} is {strServiceName}"
            txtContents.append(cont)

        self.myTitleComment(txtContents, 'udp')
        protocols = ["domain", "snmp"]
        for protocol in protocols:

            strServiceName = getservbyname(protocol, "udp")
            cont = f"* The port number for {protocol} is {strServiceName}"
            txtContents.append(cont)



        #------------------------------------------------------------------------------
        # /etc/services 파일에서 동일 포트번호를 찾아서 리턴함.
        #------------------------------------------------------------------------------
        self.myTitleComment(txtContents, 'getservbyport()')
        numbers = (20, 21, 22, 23, 25, 53, 67, 68, 80, 110, 161, 162)
        for number in numbers:
            #print("the service for", number, "is", getservbyport(number))

            strServiceName = getservbyport(number)
            cont = f"* The service for {number} is {strServiceName}"
            txtContents.append(cont)

        self.myTitleComment(txtContents, 'hostname, ip, 구글주소')
        txtContents.append(gethostname())
        txtContents.append(gethostbyname(gethostname()))
        txtContents.append(gethostbyname("google.com"))

        txtContents.append(r"c:\Windows\System32\Drivers\etc\hosts")






    def loadImageFromFile(self, dlg, file_full_name):
        # QDialog 설정


        # 버튼 추가
        #btnDialog = QPushButton("OK", dlg)
        #btnDialog.move(100, 100)
        #btnDialog.clicked.connect(dlg_close)

        # QDialog 세팅
        dlg.setWindowTitle('Dialog')
        #dlg.setWindowModality(Qt.ApplicationModal)
        dlg.resize(300, 200)
        dlg.show()


        #dlg.close()



        img_obj = QPixmap()
        img_obj.load(file_full_name)
        img_width = img_obj.width()
        img_height = img_obj.height()

        img_obj = img_obj.scaledToWidth(img_width, img_height)
        lb_img = QLabel()
        lb_img.setPixmap(img_obj)
        lb_size = QLabel(f'너비: {str(img_obj.width())}, 높이: {str(img_obj.height())}')
        lb_size.setAlignment(Qt.AlignCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(lb_img)
        vbox.addWidget(lb_size)
        dlg.setLayout(vbox)


        dlg.setWindowTitle(file_full_name)
        dlg.move(500, 500)

        dlg.show()



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ex = CMyHeader()
    ex.show()
    sys.exit(app.exec_())

