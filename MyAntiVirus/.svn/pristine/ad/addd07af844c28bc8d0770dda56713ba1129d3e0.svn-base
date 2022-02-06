from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic

import time
import imapclient
from dateutil import parser
import pyzmail #본문 해석을 도와주는 도구




my_dlg = uic.loadUiType("./ui/MyMails.ui")[0]


class CMyMails(QDialog, my_dlg):
    def __init__(self, parent=None):

        super().__init__(parent)
        self.parent = parent
        self.setupUi(self)

        self._imap = None
        self._mids = None

        self.initUI()

    #스플리터 : https://opentutorials.org/module/544/20662
    def initUI(self):
        self.setWindowTitle('MyMails')

        self.setMinimumSize(200, 200)
        self.progressBar_1.reset()

        # self.tblFiles.rowcount = 1

        self.btnLogin.clicked.connect(self.btnLogin_Click)
        self.btnView.clicked.connect(self.btnView_Click)

        self.btnDel.clicked.connect(self.btnDel_Click)
        #체크박스
        self.chkAll.clicked.connect(self.chkAll_Click)

        #self.tblMails.cellClicked.connect(self.cellClicked)
        self.tblMails.itemSelectionChanged.connect(self.tblMails_selectionChanged)

        #메일서버가 변경되면 cboFolder를 clear()한다.
        self.cboServer.currentIndexChanged.connect(self.cboServer_currentIndexChanged)

        #폴더가 변경되면 재조회

        self.cboFolders.currentIndexChanged.connect(self.cboFolders_currentIndexChanged)

        #1칼럼의 체크박스
        self.m_checkBox = []

        self.tblMails.setColumnWidth(0, 30)  # 서버구분
        self.tblMails.setColumnWidth(1, 80) #서버구분
        self.tblMails.setColumnWidth(2, 150) #날짜
        self.tblMails.setColumnWidth(3, 200) #from
        self.tblMails.setColumnWidth(4, 400) #제목

    #메일서버가 변경되면 cboFolder를 clear()한다.
    def cboServer_currentIndexChanged(self):
        self.cboFolders.clear()

    # 메일서버가 변경되면 cboFolder를 clear()한다.
    def cboFolders_currentIndexChanged(self):
        self.getMailist()

    #메일 선택시 우측 브라우저에 내용 표시
    def tblMails_selectionChanged(self):

        items = self.tblMails.selectedItems()

        #item가 없을 수 있다. 이럴 경우 종료
        if not items: return

        row = items[0].row()
        col = items[0].column()
        item = self.tblMails.item(row, 0)
        value = item.text()

        imap = self._imap

        mid = int(value)        #메일id
        rmsgs = imap.fetch(mid, ['BODY[]', 'FLAGS'])    #메일가져오기

        my_dict = rmsgs[mid]
        message = pyzmail.PyzMessage.factory(my_dict[b'BODY[]'])  # 본문 내용을 해석하자

        msg_body = ''
        #------------------------------------------------------------------------------
        # text 파트
        # ------------------------------------------------------------------------------
        if message.html_part is None and message.text_part:
            msg_body = message.text_part.get_payload().decode(message.text_part.charset)

            msg_body = msg_body.replace('\r\n', '<br>')
            msg_body = msg_body.replace('\n', '<br>')

            self.webEngineView.setHtml(msg_body)

        # ------------------------------------------------------------------------------
        # html 파트
        # ------------------------------------------------------------------------------
        if message.html_part:
            # 줄바꿈을 추가해 준다...
            if msg_body: msg_body = msg_body + '\n'

            msg_body = msg_body + message.html_part.get_payload().decode(message.html_part.charset)
            self.webEngineView.setHtml(msg_body)

        #첨부파일 다운로드
        if col == 5:
            for part in message.mailparts:
                if part.filename:
                    fileName = QFileDialog.getSaveFileName(self, 'Save file', part.filename)
                    fileName = fileName[0]
                    print('**********{}***********'.format(fileName ))
                    if fileName :
                        cont = part.get_payload()
                        # if part.type.startswith('text/'):
                        #     open(fileName , 'w').write(cont)
                        # else:
                        #     open(fileName , 'wb').write(cont)
                        open(fileName, 'wb').write(cont)

    # ------------------------------------------------------------------------------
    # * 전체 선택 / 해제
    # ------------------------------------------------------------------------------
    def chkAll_Click(self):
        print("******checked.....")
        if len(self.m_checkBox) == 0: return

        value = self.chkAll.isChecked()
        for chk in self.m_checkBox:
            chk.setChecked(value)

    # ------------------------------------------------------------------------------
    # * 로그인 정보
    # ------------------------------------------------------------------------------
    def getLoginInfo(self, serverName):
        mailAddr = ''
        mailId = ''
        mailPwd = ''

        if serverName == 'gmail':
            mailAddr = 'imap.gmail.com'
            mailId = 'hanhonghee@gmail.com'
            mailPwd = 'h!an19845'
        elif serverName == 'naver':
            mailAddr = 'imap.naver.com'
            mailId = 'hanhonghee@naver.com'
            mailPwd = 'kyr0319'
        elif serverName == 'daum':
            mailAddr = 'imap.daum.net'
            mailId = 'hanhonghee@daum.net'
            mailPwd = 'h!an19845'

        # elif serverName == 'icis':
        #     mailAddr = 'smtp.icis.co.kr'
        #     mailId = 'hanhonghee@icis.co.kr'
        #     mailPwd = 'icis0624'

        return (mailAddr, mailId, mailPwd)

    # ------------------------------------------------------------------------------
    # * 로그인
    # ------------------------------------------------------------------------------
    def btnLogin_Click(self):
        self.progressBar_1.reset()
        self.progressBar_1.setRange(0, 2)

        mailServer = self.cboServer.currentText()
        mailAddr, mailId, mailPwd = self.getLoginInfo(mailServer)

        imap = imapclient.IMAPClient(mailAddr, ssl=True)
        self.parent.statusbar.showMessage(imap.welcome.decode('utf-8'))
        self.progressBar_1.setValue(1)
        self.progressBar_1.repaint()
        
        rv = imap.login(mailId, mailPwd)
        self._imap = imap
        self.parent.statusbar.showMessage(rv.decode('utf-8'))
        self.progressBar_1.setValue(2)
        self.progressBar_1.text = "로그인 성공"

        self.showFolders()

    # ------------------------------------------------------------------------------
    # * 로그인 직후 폴더 리스트에 내용 채움
    # ------------------------------------------------------------------------------
    def showFolders(self):

        imap = self._imap

        # ------------------------------------------------------------------------------
        # * 폴더리스트를 콤보에 추가...
        # ------------------------------------------------------------------------------
        self.cboFolders.clear()
        folders = imap.list_folders()


        #빈 리스트를 하나 추가한다.
        #self.cboFolders.addItem('')

        strServer = self.cboServer.currentText()
        if strServer in ('naver', 'gmail', 'daum'):
            for i, folder in enumerate(folders):
                # ((b'\\HasNoChildren',), b'/', '통계청')
                # ((b'\\HasNoChildren', b'\\Inbox'), b'/', 'INBOX')

                Col1 = folder[0]
                name = folder[2]

                if len(Col1) > 1:
                    folder_type = Col1[1].decode('utf-8')
                    self.cboFolders.addItem('*** ' + name)

            for i, folder in enumerate(folders):
                # ((b'\\HasNoChildren',), b'/', '통계청')
                # ((b'\\HasNoChildren', b'\\Inbox'), b'/', 'INBOX')
                Col1 = folder[0]
                name = folder[2]
                if len(Col1) == 1:
                    self.cboFolders.addItem(name)

    # ------------------------------------------------------------------------------
    # * 메일 리스트 조회
    # ------------------------------------------------------------------------------
    def btnView_Click(self):
        self.getMailist()

    # ------------------------------------------------------------------------------
    # * 메일 삭제
    # ------------------------------------------------------------------------------
    def btnDel_Click(self):
        mids = []

        for row, chk in enumerate(self.m_checkBox):
            if chk.isChecked():
                cell = self.tblMails.item(row, 0)
                my = cell.text()
                mids.append(cell.text())

        if len(mids) == 0:
            self.parent.statusbar.showMessage("선택된 메일이 없습니다....")
            return

        reply = QMessageBox.question(self, '삭제확인', f'선택한 메일 총 [{len(mids)}]개를 삭제하시겠습니까?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

        if reply == QMessageBox.No:
            return

        imap = self._imap

        #요청건수
        req_cnt = len(mids)
        result = imap.delete_messages(mids)
        self.parent.statusbar.showMessage(repr(result))

        return_cnt = len(result)

        if req_cnt == return_cnt:
            QMessageBox.information(self, '삭제 성공', f"* 정상적으로 삭제되었습니다. \n* 총 요청 [{req_cnt}]건 삭제된 건수[{req_cnt}]")

            row = 0
            for chk in self.m_checkBox:
                if chk.isChecked():
                    self.tblMails.removeRow(row)
                else:
                    row += 1

            # 삭제후 다시 체크박스 리스트를 만든다.
            self.insertCheckBoxToTable()


        else:
            QMessageBox.information(self, '삭제 오류', f"* 삭제 오류가 발생했습니다. \n* 총 요청 [{req_cnt}]건 삭제된 건수[{req_cnt}]")
            return

        rtn = imap.expunge()
        self.parent.statusbar.showMessage(repr(rtn))

        print('****메일 삭제....')

    #------------------------------------------------------------------------------
    #* 메일 리스트 조회
    # ------------------------------------------------------------------------------
    def getMailist(self):
        self.progressBar_1.reset()

        self.tblMails.setRowCount(0)


        imap = self._imap

        folder_name = self.cboFolders.currentText()
        folder_name = folder_name.replace('*** ', '')

        if folder_name:
            #folder = imap.select_folder('INBOX', readonly=False)
            #folder = imap.select_folder('[Gmail]/전체보관함', readonly=False)

            folder = imap.select_folder(folder_name, readonly=False)
            print(folder)

        kw = self.edSearchKeyword.text()

        #검색어가 없을 경우는 'ALL'로 전체검색을 수행한다.
        arr = ['ALL']
        if kw.strip() != '':
            arr = ['OR', 'FROM', kw, 'SUBJECT', kw, 'BODY', kw]


        mids = imap.search(arr, charset='UTF-8')

        #print('*****************status : ', status)
        self.progressBar_1.setRange(0, len(mids))

        row = 0
        for mid in mids:
            rmsgs = imap.fetch(mid, ['BODY[]', 'FLAGS'])

            # pyzmail : 본문해석을 도와주는 도구...
            message = pyzmail.PyzMessage.factory(rmsgs[mid][b'BODY[]'])  # 본문 내용을 해석하자

            # 그리드에 메일 리스트를 채운다.
            self.showDataToTable(message, row, mid)

            #time.sleep(0.1)

            #if row> 5: break

            row += 1
            self.progressBar_1.setValue(row)


        #체크박스 넣기...
        self.insertCheckBoxToTable()

    #검색어 배열을 규칙에 맞게 만든다.
    def makeSearchArray(self, search_keyword):
        searchArrary = []
        searchArrary.append('OR')
        #['OR', ['FROM', 'hanhonghee'], ['TEXT', 'hanhonghee']]

        search_keyword = search_keyword.encode('utf-8')

        unit = ['FROM', search_keyword]


        divs = [u'FROM', u'TO', u'CC', u'SUBJECT', u'BODY']
        for div in divs:
            unit = [div, search_keyword]
            searchArrary.append(unit)

        return searchArrary

    # ------------------------------------------------------------------------------
    # * 그리드에 메일 리스트를 채운다.
    # ------------------------------------------------------------------------------
    def showDataToTable(self, message, row, mid):
        mail_subject = message.get_subject()
        mail_from = message.get_address('from')
        mail_to = message.get_address('to')  # 수신자 정보
        mail_cc = message.get_address('cc')  # 참조


        dt = message.get('Date')

        #pyzmail에 Date 버그가 있다.
        if dt is not None:
            date = parser.parse(dt)
            dt = date.strftime('%Y-%m-%d(%a) %H:%M')

        else:
            dt = "-"

        #첨부파일
        attach_cnt = 0

        for part in message.mailparts:
            if part.filename:
                attach_cnt += 1

        self.tblMails.setRowCount(row + 1)

        print('******** ', type(mid))

        # item = QTableWidgetItem()
        # item.setData = (Qt.DisplayRole, mid)

        #mid
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, mid)
        item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.tblMails.setItem(row, 0, item)


        # ------------------------------------------------------------------------------
        # * 새로 추가되는 아이템이 화면에 보이게 처리....
        # ------------------------------------------------------------------------------
        self.tblMails.scrollToItem(item)
        self.tblMails.selectRow(row + 1)

        # 서버구분
        self.insertDataToTable(row, 1, self.cboServer.currentText(), Qt.AlignVCenter | Qt.AlignCenter)

        # 일시
        self.insertDataToTable(row, 2, dt, Qt.AlignVCenter | Qt.AlignCenter)

        #발신자
        self.insertDataToTable(row, 3, mail_from[0] + '(' + mail_from[1] + ')', Qt.AlignVCenter | Qt.AlignLeft)

        #제목
        self.insertDataToTable(row, 4, mail_subject, Qt.AlignVCenter | Qt.AlignLeft)

        #첨부파일
        self.insertDataToTable(row, 5, str(attach_cnt), Qt.AlignVCenter | Qt.AlignCenter)


        self.tblMails.repaint()

    def insertDataToTable(self, row, col, data, align):
        item = QTableWidgetItem(data)
        item.setTextAlignment(align)
        self.tblMails.setItem(row, col, item)

    def insertCheckBoxToTable(self):

        self.m_checkBox = []
        self.numRow = self.tblMails.rowCount()
        for i in range(self.numRow):
            ckbox = QCheckBox()
            ckbox.setChecked(True)
            self.m_checkBox.append(ckbox)

        for i in range(self.numRow):
            cellWidget = QWidget()
            layoutCB = QHBoxLayout(cellWidget)
            layoutCB.addWidget(self.m_checkBox[i])
            layoutCB.setAlignment(Qt.AlignCenter)
            layoutCB.setContentsMargins(0, 0, 0, 0)
            cellWidget.setLayout(layoutCB)

            # self.tableWidget.setCellWidget(i,0,self.checkBoxList[i])
            self.tblMails.setCellWidget(i, 0, cellWidget)

    def showMail(self, mid):
        pass

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ex = CMyMails()
    ex.show()
    sys.exit(app.exec_())

