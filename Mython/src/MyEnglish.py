from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic

import PyQt5.QtGui



import time
import random
from datetime import datetime
import sqlite3

from collections import OrderedDict

import re

CHROME_DRIVER_PATH = "D:/driver/chromedriver_97.exe"
GOOGLE_TRANSLATE_URL = "https://translate.google.co.kr/?sl=en&tl=ko&text="
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


# element 로딩완료 대기
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from urllib import parse


#영어회화 100일의 기적 2 : https://www.youtube.com/user/muncoach/videos

'''
* 파이썬 ui 참고 자료 - wikidoc
- PyQt5 Tutorial - 파이썬으로 만드는 나만의 GUI 프로그램
- 초보자를 위한 Python GUI 프로그래밍 - PyQt5
- python_ Cheat Sheet
- 영어 말하기 스크랩 당장 할것 : https://www.englisch-hilfen.de/en/words/uhr.htm
'''


# 책 https://English.net/book/1
# 책 - 챕터 https://English.net/2
g_url = 'https://English.net'



my_dlg = uic.loadUiType("./ui/MyEnglish.ui")[0]


con = sqlite3.connect("./English.db")

all_book_lists = []


class CMyEnglish(QDialog, my_dlg):
    def __init__(self, parent=None):
        print("parent:", parent)
        self.myParent = parent
        super().__init__(parent)
        self.setupUi(self)
        # loadUi("test2",self)

        self.book_id = -1
        self.chapter_id = -1

        # edit과 라벨을 리스트로 담아서 처리...
        self.widget_list_edit = []
        self.widget_list_label = []

        #* 콘트롤을 배열로 관리.
        self.f_make_widget_array()

        self.contentsDict = OrderedDict()

        # 실패 횟수
        self.fail_count = 0

        self.intFrom = None
        self.intTo = None

        self.intSuccessCount = 0  # 성공 카운트 누적....
        self.intTargetCount = 100

        self.btnStart.clicked.connect(self.btnStart_Click)
        self.cboBooks.currentIndexChanged.connect(self.cboBooks_IndexChanged)
        self.lstChapters.currentItemChanged.connect(self.lstChpaters_currentItemChanged)

        self.txtMyAnswer_1.returnPressed.connect(self.txtMyAnswer_1_returnPressed)
        self.txtMyAnswer_2.returnPressed.connect(self.txtMyAnswer_2_returnPressed)
        self.txtMyAnswer_3.returnPressed.connect(self.txtMyAnswer_3_returnPressed)
        self.txtMyAnswer_4.returnPressed.connect(self.txtMyAnswer_4_returnPressed)
        self.txtMyAnswer_5.returnPressed.connect(self.txtMyAnswer_5_returnPressed)
        self.txtMyAnswer_6.returnPressed.connect(self.txtMyAnswer_6_returnPressed)

        self.initUI()

        self.optModeTest.setChecked(True)


        # 크롬 열기
        self.driver = None
        self.btnOpenChrome.clicked.connect(self.btnOpenChrome_Click)

        # 숨기기 버튼 연결
        self.btnHide.clicked.connect(self.btnHide_Click)
        self.btnReloadContents.clicked.connect(self.btnReloadContents_Click)

        self.btnSaveStatus.clicked.connect(self.btnSaveStatus_Click)
        self.btnLoadStatus.clicked.connect(self.btnLoadStatus_Click)



        # item = self.lstChapters.item(0)
        # item.setForeground(PyQt5.QtGui.QColor('gray'))
        #
        # item = self.lstChapters.item(1)
        # item.setForeground(PyQt5.QtGui.QColor('gray'))
        #
        # item = self.lstChapters.item(2)
        # item.setForeground(PyQt5.QtGui.QColor('gray'))
        #
        # item = self.lstChapters.item(98)
        # item.setForeground(PyQt5.QtGui.QColor('gray'))
        #
        # item = self.lstChapters.item(99)
        # item.setForeground(PyQt5.QtGui.QColor('gray'))

    def f_openChrome(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-extensions')  # 확장 프로그램 구동 정지
        # options.add_argument('--start-maximized')  # 최대 크기 윈도우로 시작

        # options.add_argument('window-size=1200x600') #윈도우 크기 지정
        # options.headless = True    #윈도우가 눈에 보이지 않게 실행

        self.driver = webdriver.Chrome(options=options, executable_path=CHROME_DRIVER_PATH)

        self.startUrl = GOOGLE_TRANSLATE_URL  # 구글 번역 사이트
        self.driver.get(self.startUrl)

        # self.driver.get("https://cafe.naver.com/graydidrb")

        # time.sleep(1)
        #
        # id = self.driver.find_element_by_id("id")
        # strName = "hanhonghee"
        # for i in range(len(strName)):
        #     id.send_keys(strName[i])
        #     time.sleep(0.01)
        #
        # pw = self.driver.find_element_by_id("pw")
        # strPwd = "kyr0319"
        # for i in range(len(strPwd)):
        #     pw.send_keys(strPwd[i])
        #     time.sleep(0.01)

    def btnOpenChrome_Click(self):
        self.f_openChrome()

    def f_make_widget_array(self):
        self.widget_list_edit.append(self.txtMyAnswer_1)
        self.widget_list_edit.append(self.txtMyAnswer_2)
        self.widget_list_edit.append(self.txtMyAnswer_3)
        self.widget_list_edit.append(self.txtMyAnswer_4)
        self.widget_list_edit.append(self.txtMyAnswer_5)
        self.widget_list_edit.append(self.txtMyAnswer_6)

        self.widget_list_label.append(self.lblResult_1)
        self.widget_list_label.append(self.lblResult_2)
        self.widget_list_label.append(self.lblResult_3)
        self.widget_list_label.append(self.lblResult_4)
        self.widget_list_label.append(self.lblResult_5)
        self.widget_list_label.append(self.lblResult_6)

    def txtMyAnswer_1_returnPressed(self):
        self.f_check_answer(1, self.txtMyAnswer_1, self.lblResult_1)

    def txtMyAnswer_2_returnPressed(self):
        self.f_check_answer(2, self.txtMyAnswer_2, self.lblResult_2)


    def txtMyAnswer_3_returnPressed(self):
        self.f_check_answer(3, self.txtMyAnswer_3, self.lblResult_3)

    def txtMyAnswer_4_returnPressed(self):
        self.f_check_answer(4, self.txtMyAnswer_4, self.lblResult_4)

    def txtMyAnswer_5_returnPressed(self):
        self.f_check_answer(5, self.txtMyAnswer_5, self.lblResult_5)

    def txtMyAnswer_6_returnPressed(self):
        self.f_check_answer(6, self.txtMyAnswer_6, self.lblResult_6)



    # 챕터 리스트 선택 변경
    def lstChpaters_currentItemChanged(self):

        # 1. 현재 선택된 book_id 가져오기
        self.book_id = self.cboBooks.itemData(self.cboBooks.currentIndex())

        # 2. 선택된 챕터 정보 가져오기
        curIndex = self.lstChapters.currentRow()

        if curIndex < 0:
            return

        #------------------------------------------------------------------------------
        # 챕터 id / 챕터 명
        # ------------------------------------------------------------------------------
        self.chapter_id = curIndex + 1 # db는 1 base

        item = self.lstChapters.currentItem()
        self.chapter_name = item.text()


        self.f_get_contents(self.book_id, self.chapter_id)

        # 3. 대답영역 초기화...
        self.f_init_answer_textbox()

        # 3.1 Answer Textbox placeholder text
        self.f_set_placeholderText()

        # 4. 첫번째 에디트에 포커스
        self.f_ready_next(self.widget_list_edit[0], self.widget_list_label[0])


        #------------------------------------------------------------------------------
        #* 챕터 id/ 챕터 명
        # ------------------------------------------------------------------------------
        self.txtChapterId.setText(str(self.chapter_id))
        self.txtChapterName.setText(self.chapter_name)

        #RangeTo에 현재 id 넣기
        #self.txtTo.setText(str(self.chapter_id))

    def f_init_answer_textbox(self):
        myList = list(self.contentsDict.values())

        for idx, edit in enumerate(self.widget_list_edit):
            edit.setText("")

        for label in self.widget_list_label:
            label.setText("")

    def f_set_placeholderText(self):
        myList = list(self.contentsDict.values())

        for idx, edit in enumerate(self.widget_list_edit):
            (_, _, placeholderText) = myList[idx]
            edit.setPlaceholderText(placeholderText)

    def f_save_chapter(self, book_id, chapter_id, chapter_name):
        sql = "delete from book_chapters where book_id = ? and chapter_id = ?"
        con.execute(sql, (book_id, chapter_id))

        sql = """
                insert into book_chapters (book_id, chapter_id, ord, 
                                           chapter_div, chapter_nm, use_yn )
                values(?, ?, ?, ?, ?, ?)                             
        """

        #Day 001. 봄꽃나들이
        chapter_div = chapter_name[:7].strip()        #Day 001
        chapter_nm = chapter_name[8:].strip()         #봄꽃나들이


        con.execute(sql, (book_id, chapter_id, chapter_id,
                          chapter_div, chapter_nm, 'Y'))


    def f_save_contents(self, lblWidget, txtWidget, book_id, chapter_id, contents_id):

        sql = "delete from book_contents where book_id = ? and chapter_id = ? and contents_id = ?"
        con.execute(sql, (book_id, chapter_id, contents_id))


        sql = """
                        insert into book_contents (book_id, chapter_id, contents_id, ord, 
                                                   contents_1, contents_2)
                        values(?, ?, ?, ?, ?, ?)                             
                """

        # Day 001. 봄꽃나들이
        contents_1 = lblWidget.text()
        contents_2 = txtWidget.text()


        con.execute(sql, (book_id, chapter_id, contents_id, contents_id,
                          contents_1, contents_2))


    def f_save(self):
        book_id = self.txtBookId.text()
        chapter_id = self.txtChapterId.text()
        chapter_name = self.txtChapterName.text()

        self.f_save_chapter(book_id, chapter_id, chapter_name)

        self.f_save_contents(self.lblSpeaker_1, self.txtMyAnswer_1, book_id, chapter_id, 1)
        self.f_save_contents(self.lblSpeaker_2, self.txtMyAnswer_2, book_id, chapter_id, 2)
        self.f_save_contents(self.lblSpeaker_3, self.txtMyAnswer_3, book_id, chapter_id, 3)
        self.f_save_contents(self.lblSpeaker_4, self.txtMyAnswer_4, book_id, chapter_id, 4)
        self.f_save_contents(self.lblSpeaker_5, self.txtMyAnswer_5, book_id, chapter_id, 5)
        self.f_save_contents(self.lblSpeaker_6, self.txtMyAnswer_6, book_id, chapter_id, 6)

        con.commit()

        QMessageBox.information(self, '성공', "정상 저장되었습니다.", QMessageBox.Yes)



    def f_clear_txtWdiget(self):
        for txt in self.widget_list_edit:
            txt.clear()

    #정답 비교, index 1 base
    def f_check_answer(self, index, txtMyAnswer, lblResult):

        book_id = self.txtBookId.text()
        chapter_id = self.txtChapterId.text()

        #저장모드인 경우 저장한다.
        if self.optModeSave.isChecked():

            #index가 6인 경우 저장
            if index >= 6:
                if QMessageBox.Yes == QMessageBox.information(self, '저장', "저장하시겠습니까?", QMessageBox.Yes | QMessageBox.No):
                    self.f_save()

                    # 내용 텍스트 박스 클리어
                    self.f_clear_txtWdiget()

                    # 챕터 텍스트 박스 클리어
                    self.txtChapterId.clear()
                    self.txtChapterName.clear()

                    # 챕터 id set focus
                    self.txtChapterId.setFocus()

            else:

                self.widget_list_edit[index].setFocus()

            return

        #1. 내 답 대문자, 공백제거
        strAnswer_origin = txtMyAnswer.text()
        strMyAnswer = self.f_convert_for_comp(strAnswer_origin)

        #2. 정답 가져오기
        (strPrefix, strText, strPlaceHolderText) = list(self.contentsDict.values())[:index][-1]

        #3. 정답  대문자, 공백제거
        strBookAnswer = self.f_convert_for_comp(strText)

        #4. 정답비교
        if strMyAnswer == strBookAnswer:

            self.f_save_answer_result(book_id, chapter_id, index, 'Y', None, None)

            # 오답 회수 초기화...
            self.fail_count = 0

            # 1. 정답처리
            lblResult.setText("정답")

            # 영어로 speak하기
            self.f_speak_english_sentence(strAnswer_origin)

            # edit과 라벨을 리스트로 담아서 처리...
            if index < len(self.contentsDict):
                # index가 one base이므로 걍 index 해서 넣어주면 된다.
                self.f_ready_next(self.widget_list_edit[index], self.widget_list_label[index])
            else:

                curIndex = self.lstChapters.currentRow()
                item = self.lstChapters.item(curIndex)
                item.setForeground(PyQt5.QtGui.QColor('gray'))


                msg = "이번 챕터 성공입니다. 다음 챕터로 넘어갈까요?"
                rtn = QMessageBox.information(self, '성공', msg, QMessageBox.Yes | QMessageBox.No | QMessageBox.Retry)
                if QMessageBox.Yes == rtn:

                    # 성공 누적 수량 증가
                    self.intSuccessCount += 1

                    # 목표 수량 체크
                    if self.intSuccessCount >= self.intTargetCount:
                        QMessageBox.information(self, '축하', f"축하해요. 목표수량 [{self.intSuccessCount}]개를 모두 성공했어요~~~~", QMessageBox.Yes)
                        return

                    # ------------------------------------------------------------------------------
                    #* 다음 챕터 가져오기.
                    # ------------------------------------------------------------------------------
                    item = self.f_next_chapter()
                    if item == None:
                        QMessageBox.information(self, '축하', "축하해요. 모든 챕터를 성공했어요~~~~", QMessageBox.Yes)
                    else:
                        self.lstChapters.setCurrentItem(item)
                elif rtn == QMessageBox.No:
                    # Answer Textbox 초기화
                    self.f_init_answer_textbox()

                    # 4. 첫번째 혹은 마지막 에디트에 포커스
                    self.f_ready_next(self.widget_list_edit[0], self.widget_list_label[0])

                #------------------------------------------------------------------------------
                #* 마지막 문장 다시 도전
                #------------------------------------------------------------------------------
                elif rtn == QMessageBox.Retry:
                    self.widget_list_edit[5].setText("")
                    self.widget_list_label[5].setText("")

                    # 4. 첫번째 혹은 마지막 에디트에 포커스
                    self.f_ready_next(self.widget_list_edit[5], self.widget_list_label[5])

        else:
            lblResult.setText("오답")

            strMyAnswer_NoSpecialChar = re.sub(r'[^a-zA-Z0-9]', '', strMyAnswer)
            strBookAnswer_NoSpecialChar = re.sub(r'[^a-zA-Z0-9]', '', strBookAnswer)

            fail_type = '오답'
            if self.fail_count <= 2 and \
                    strMyAnswer_NoSpecialChar == strBookAnswer_NoSpecialChar:
                msg = "다 맞고 문장부호만 틀림!!!"
                QMessageBox.information(self, '문장부호 확인', msg, QMessageBox.Yes)
                self.fail_count += 1
                fail_type = '문장부호만 틀림'

            elif self.fail_count >= 2:
                msg = "틀렸습니다.... 정답은 다음과 같습니다.\n"
                msg = msg + "\n* 정답 : " + strText
                msg = msg + "\n* 입력 : " + strAnswer_origin
                QMessageBox.critical(self, '정답 제공', msg, QMessageBox.Yes)

                self.fail_count = 0
            else:
                QMessageBox.critical(self, '오답', "틀렸습니다.... 다시 도전하시겠습니까?", QMessageBox.Yes)
                lblResult.setText("☜")
                self.fail_count += 1

            self.f_save_answer_result(book_id, chapter_id, index, 'N', fail_type, strAnswer_origin)

    def f_save_answer_result(self, book_id, chapter_id, index, success_yn, fail_type, answer_text):

        sql = """
                    insert into book_test(TestDay, TestTime, book_id, chapter_id, contents_id, success_YN, fail_type, answer_text)
                    values (?,?,?,?,?,?,?,?)                          
                """

        # 로딩시 오늘을 기본값으로 넣어줌
        strToday = datetime.today().strftime("%Y-%m-%d")
        strTime = datetime.today().strftime("%H:%M:%S")


        con.execute(sql, (strToday, strTime, book_id, chapter_id, index,
                          success_yn, fail_type, answer_text))

        con.commit()


    def f_speak_english_sentence(self, strSentence):
        enc = parse.quote(strSentence)
        GOOGLE_TRANSLATE_URL = "https://translate.google.co.kr/?sl=en&tl=ko&text="
        strUrl = GOOGLE_TRANSLATE_URL + enc

        if not self.driver:
            self.f_openChrome()
            time.sleep(3)


        self.driver.get(strUrl)
        WebDriverWait(self.driver, 60 * 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".VfPpkd-Bz112c-LgbsSe.fzRBVc.tmJved.SSgGrd.m0Qfkd"))
        )

        my_btn = self.driver.find_element_by_css_selector(".VfPpkd-Bz112c-LgbsSe.fzRBVc.tmJved.SSgGrd.m0Qfkd")
        #time.sleep(1)
        my_btn.send_keys(Keys.RETURN)

        #self.driver.implicitly_wait(10)
        #ActionChains(self.driver).move_to_element(my_btn).click(my_btn).perform()



    #다음 문장 입력 대기
    def f_ready_next(self, edit_next, label_next):

        edit_next.setText("")
        edit_next.setFocus()

        label_next.setText("☜")


    #정답 비교용. 공백제거 대문자
    def f_convert_for_comp(self, str):
        strReturn = str
        strReturn = strReturn.strip()
        strReturn = strReturn.upper()
        strReturn = strReturn.replace(' ', '')

        return strReturn


    def cboBooks_IndexChanged(self):
        strBook = self.cboBooks.currentText()

        # 1. 현재 선택된 book_id 가져오기
        self.book_name = self.cboBooks.currentText()
        self.book_id = self.cboBooks.itemData(self.cboBooks.currentIndex())
        self.f_add_book_chapters_to_list(self.book_id)


        self.lblBookName.setText(self.book_name)
        self.txtBookId.setText(str(self.book_id))

    def btnReloadContents_Click(self):
        self.f_get_contents(self.book_id, self.chapter_id)

        #3.1 Answer Textbox placeholder text
        self.f_set_placeholderText()

    # ------------------------------------------------------------------------------
    # * 저장된 상태 불러오기
    # ------------------------------------------------------------------------------
    def btnLoadStatus_Click(self):
        # ------------------------------------------------------------------------------
        # 1. 책 테스트 상태 불러오기
        # ------------------------------------------------------------------------------
        cursor = con.cursor()
        sql = """
                    select book_id, chapter_id, chapter_name, test_mode,
                            test_direction, test_from_chapter, test_to_chapter
                      from saved_status
                    where 1=1
                      and book_id = ?
                    order by 1
                        """
        cursor.execute(sql, (self.book_id,))

        row = cursor.fetchone()

        #book_id = row[0]
        self.chapter_id = row[1]
        self.chapter_name = row[2]
        test_mode = row[3]
        test_direction = row[4]
        test_from_chapter = str(row[5])
        test_to_chapter = str(row[6])

        self.txtBookId.setText(str(self.book_id))
        self.txtChapterId.setText(str(self.chapter_id))
        self.txtChapterName.setText(self.chapter_name)

        if test_mode == "테스트 모드":
            self.optModeTest.setChecked(True)
        elif test_mode == "저장 모드":
            self.optModeSave.setChecked(True)

        if test_direction == "정방향":
            self.optDirection_1.setChecked(True)
        elif test_direction == "역방향":
            self.optDirection_2.setChecked(True)
        elif test_direction == "Random":
            self.optDirection_3.setChecked(True)

        self.txtFrom.setText(test_from_chapter)
        self.txtTo.setText(test_to_chapter)

        #해당 챕터를 활성화
        item = self.lstChapters.item(self.chapter_id - 1) #콘트롤은 제로 base
        self.lstChapters.setCurrentItem(item)

        # ------------------------------------------------------------------------------
        # * 2. 책 챕터 리스트 불러오기
        # ------------------------------------------------------------------------------
        sql = """
                        select book_id, chapter_id
                          from saved_status_chapters
                        where 1=1
                          and book_id = ?
                          and test_yn = 'Y'
                        order by book_id, chapter_id
                        """
        cursor.execute(sql, (self.book_id,))

        #------------------------------------------------------------------------------
        #* 모두 검정으로 초기화
        # ------------------------------------------------------------------------------
        list_cnt = self.lstChapters.count()

        for i in range(list_cnt):
            item = self.lstChapters.item(i)
            item.setForeground(PyQt5.QtGui.QColor('black'))

        for row in cursor.fetchall():
            chapter_id = row[1]

            chapter_id = chapter_id -1 #  Zero base

            item = self.lstChapters.item(chapter_id)
            item.setForeground(PyQt5.QtGui.QColor('gray'))



        cursor.close()

    #------------------------------------------------------------------------------
    #* 현재 상태 저장
    #------------------------------------------------------------------------------
    def btnSaveStatus_Click(self):
        test_mode = ""
        if self.optModeTest.isChecked():
            test_mode = "테스트 모드"
        elif self.optModeSave.isChecked():
            test_mode = "저장 모드"

        test_direction = ""
        if self.optDirection_1.isChecked():
            test_direction = "정방향"
        elif self.optDirection_2.isChecked():
            test_direction = "역방향"
        elif self.optDirection_3.isChecked():
            test_direction = "Random"

        test_from_chapter = self.txtFrom.text()
        test_to_chapter = self.txtTo.text()

        self.f_save_status(self.book_id, self.chapter_id, self.chapter_name, test_mode,
                     test_direction, test_from_chapter, test_to_chapter)

        chapter_ids = []
        #리스트 챕터
        list_cnt = self.lstChapters.count()

        for i in range(list_cnt):
            item = self.lstChapters.item(i)
            color = item.foreground()

            #회색
            if color == PyQt5.QtGui.QColor('gray'):
                chapter_ids.append(i + 1) #리스트콘트롤 : 0 base db: 1 base

        if len(chapter_ids) > 0:
            self.f_save_status_chapters(self.book_id, chapter_ids)

        con.execute("commit")

    # 현재 화면 상태 저장하기
    def f_save_status(self, book_id, chapter_id, chapter_name, test_mode,
                     test_direction, test_from_chapter, test_to_chapter):

        sql = "delete from saved_status where book_id = ?"
        con.execute(sql, (book_id,))


        sql = """
            insert into saved_status(book_id, chapter_id, chapter_name, test_mode, 
                                        test_direction, test_from_chapter, test_to_chapter)
            values (?, ?, ?, ?, ?, ?, ?)
        """
        con.execute(sql, (book_id, chapter_id, chapter_name, test_mode,
                     test_direction, test_from_chapter, test_to_chapter))

    #현재 화면상태 - 리스트 상태 저장하기
    def f_save_status_chapters(self, book_id, chapter_ids):
        sql = "delete from saved_status_chapters where book_id = ?"
        con.execute(sql, (book_id,))

        for chapter_id in chapter_ids:
            sql = """
                insert into saved_status_chapters(book_id, chapter_id, test_yn)
                values(?, ?, 'Y')
            """
            con.execute(sql, (book_id, chapter_id))

    def btnHide_Click(self):
        blnShow = False

        if self.btnHide.text() == "숨기기":
            self.btnHide.setText("보이기")
            self.myParent.resize(638, 354)
            blnShow = False

        else:
            self.btnHide.setText("숨기기")
            self.myParent.resize(946, 525)
            blnShow = True

        self.btnHide.setShortcut("F4")

        self.lblBookID.setVisible(blnShow)
        self.cboBooks.setVisible(blnShow)

        self.lstChapters.setVisible(blnShow)
        self.lblBookName.setVisible(blnShow)


        self.groupBox.setVisible(blnShow)
        self.groupBox_2.setVisible(blnShow)
        self.groupBox_3.setVisible(blnShow)

        self.txtHistory.setVisible(blnShow)

    def btnStart_Click(self):

        cnt = self.lstChapters.count()
        if cnt == 0:
            QMessageBox.critical(self, '데이터 확인', "리스트가 비었습니다. 시작할 수 없습니다.", QMessageBox.Yes)
            return
        #------------------------------------------------------------------------------
        # 테스트 목표 수량
        # ------------------------------------------------------------------------------
        strTargetCount = self.txtTargetCount.text()
        if not strTargetCount.isdecimal():
            QMessageBox.information(self, '성공', '목표 수량을 정수형으로 입력하세요.', QMessageBox.Yes)
            self.txtTargetCount.setFocus()
            return

        self.intTargetCount = int(strTargetCount)
        self.intSuccessCount = 0 #성공 카운트 누적....

        # ------------------------------------------------------------------------------
        # 테스트 시작 ~ 끝
        # ------------------------------------------------------------------------------
        strFrom = self.txtFrom.text()
        strTo = self.txtTo.text()

        if not strFrom.isdecimal():
            QMessageBox.information(self, '성공', 'Range의 시작을 정수형으로 입력하세요.', QMessageBox.Yes)
            self.txtFrom.setFocus()
            return

        if not strTo.isdecimal():
            QMessageBox.information(self, '성공', 'Range의 시작을 정수형으로 입력하세요.', QMessageBox.Yes)
            self.strTo.setFocus()
            return

        intFrom = int(strFrom)
        intTo = int(strTo)

        # 리스트의 인덱스는 zero base임. 시작에서 1을 빼준다.
        intFrom = intFrom - 1


        # 멤버 변수로 보관...
        self.intFrom = intFrom
        self.intTo = intTo

        if intFrom > intTo:
            QMessageBox.critical(self, '데이터 확인', f"시작챕터가 종료 챕터보다 큽니다.시작[{intFrom}], 종료[{intTo}]", QMessageBox.Yes)
            return
        elif intFrom > 100:
            QMessageBox.critical(self, '데이터 확인', f"시작챕터는 100보다 클 수 없습니다. 지금 시작값 [{intFrom}]", QMessageBox.Yes)
            return

        QMessageBox.information(self, '게임 시작', "지금부터 게임을 시작합니다.", QMessageBox.Yes)

        #다음 챕터 가져오기
        item = self.f_next_chapter()
        self.lstChapters.setCurrentItem(item)

    # 다음 챕터 가져오기
    def f_next_chapter(self):

        strFrom = self.txtFrom.text()
        strTo = self.txtTo.text()

        self.intFrom = int(strFrom)
        self.intTo = int(strTo)


        # 안한 챕터가 있는지 확인
        list_cnt = self.lstChapters.count()

        # gray 개수 count 하기....
        gray_cnt = 0
        for i in range(list_cnt):
            item = self.lstChapters.item(i)
            color = item.foreground()

            # 회색 카운트 증가
            if color == PyQt5.QtGui.QColor('gray'):
                gray_cnt += 1

        # 회색이 리스트 카운트보다 많으면 모두 처리한 것임....
        if gray_cnt >= list_cnt:
            return None

        if self.optDirection_1.isChecked(): #정방향
            item = self.f_next_chapter_move(1)
            return item
        elif self.optDirection_2.isChecked():  # 역방향
            item = self.f_next_chapter_move(-1)
            return item
        elif self.optDirection_3.isChecked():
            item = self.f_next_chapter_random(self.intFrom, self.intTo)
            return item



    #정방향
    def f_next_chapter_move(self, move):
        curIndex = self.lstChapters.currentRow()

        nowIndex = curIndex

        while True:
            nowIndex += move

            #마지막 아이템이면 종료
            if nowIndex >= self.lstChapters.count():
                return None

            item = self.lstChapters.item(nowIndex)
            color = item.foreground()

            # 회색이면 continue
            if color == PyQt5.QtGui.QColor('gray'):
                continue

            # 회색이 아니다. 다음 아이템 선택
            item = self.lstChapters.item(nowIndex)
            #self.lstChapters.setCurrentItem(item)

            return item


    #random
    def f_next_chapter_random(self, intFrom, intTo):

        list_cnt = self.lstChapters.count()

        # from ~ to 다 했으면 종료
        blnDone = True
        for index in range(intFrom, intTo):
            item = self.lstChapters.item(index)
            color = item.foreground()

            # 처리 안한 게 있는지 확인.
            if color != PyQt5.QtGui.QColor('gray'):
                blnDone = False
                break

        # 모두 처리함. return
        if blnDone:
            return None

        # 안한 챕터 찾기
        while True:

            index = random.randrange(intFrom, intTo)

            item = self.lstChapters.item(index)
            color = item.foreground()

            # 처리 안한 item만 뽑기...
            if color != PyQt5.QtGui.QColor('gray'):
                item = self.lstChapters.item(index)
                #self.lstChapters.setCurrentItem(item)

                return item

    def initUI(self):
        self.setWindowTitle('MyEnglish')

        self.f_add_books_to_combo()

    # 리스트에 챕터 추가
    def f_get_contents(self, book_id, chapter_id):

        self.contentsDict.clear()

        # 1. db에서 읽어온다.
        cursor = con.cursor()
        sql = """
                select contents_id, contents_1, contents_2, contents_3
                  from book_contents
                where 1=1
                  and book_id = ?
                  and chapter_id = ?
                order by ord
                """
        cursor.execute(sql, (book_id, chapter_id))

        for row in cursor.fetchall():
            book_id = row[0]
            contents_1 = row[1]
            contents_2 = row[2]
            contents_3 = row[3]

            self.contentsDict[book_id] = [contents_1, contents_2, contents_3]

        cursor.close()

        return self.contentsDict

    #리스트에 챕터 추가
    def f_add_book_chapters_to_list(self, book_id):
        self.lstChapters.clear()

        # 1. db에서 읽어온다.
        cursor = con.cursor()
        sql = """
                select chapter_div || '. ' || chapter_nm as chapter
                  from book_chapters
                where use_yn = ?
                  and book_id = ?
                order by ord
                """
        cursor.execute(sql, ('Y', book_id))


        for row in cursor.fetchall():
            item = QListWidgetItem(row[0])
            self.lstChapters.addItem(item)

        row_cnt = len(self.lstChapters)
        if row_cnt > 0 :
            item = self.lstChapters.item(0)
            self.lstChapters.setCurrentItem(item)

        cursor.close()

    def f_add_books_to_combo(self):
        # 1. db에서 읽어온다.
        cursor = con.cursor()
        sql = """
                select book_id, book_name
                  from books
                where use_yn = ?
                order by ord
                """
        cursor.execute(sql, ('Y',))


        index = 0
        for row in cursor.fetchall():
            self.cboBooks.addItem(row[1])
            self.cboBooks.setItemData(index, row[0]) #book_id를 itemData에 저장

            index += 1

        self.cboBooks.setCurrentIndex(-1)
        self.cboBooks.setCurrentIndex(0)
        cursor.close()

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ex = CMyEnglish()
    ex.show()
    sys.exit(app.exec_())

