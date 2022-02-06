from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
import win32com.client


import requests
from bs4 import BeautifulSoup
import re
import time
import random
from datetime import datetime
import sqlite3


import urllib.parse #url 한글깨짐을 원래대로 보기 위해...


from src.MyHtmlClipboard import *
from src.MyImageClipboard import *


from selenium import webdriver
from selenium.webdriver.common.keys import Keys


# element 로딩완료 대기
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ctrl+v용
from selenium.webdriver.common.action_chains import ActionChains

# 예외 처리용. <class 'selenium.common.exceptions.UnexpectedAlertPresentException'>
from selenium.common.exceptions import UnexpectedAlertPresentException

# clipboard tstory용
#import clipboard
import pyperclip

# img 저장용
import urllib.request



# img clipboard 처리용
from io import BytesIO
import win32clipboard
from PIL import Image

'''
* 파이썬 ui 참고 자료 - wikidoc
- PyQt5 Tutorial - 파이썬으로 만드는 나만의 GUI 프로그램
- 초보자를 위한 Python GUI 프로그래밍 - PyQt5
- python_ Cheat Sheet
'''


# 책 https://wikidocs.net/book/1
# 책 - 챕터 https://wikidocs.net/2
g_url = 'https://wikidocs.net'



my_dlg = uic.loadUiType("./ui/MyWikiDocs.ui")[0]


con = sqlite3.connect("./books.db")

all_book_lists = []


class CMyWikiDocs(QDialog, my_dlg):
    def __init__(self, parent=None):
        print("parent:", parent)
        super().__init__(parent)
        self.setupUi(self)
        # loadUi("test2",self)

        self.initUI()

        #* 현재 작업 상태 가져오기
        self.f_get_work_status()

        #* 책 정보 조회
        self.btnView.clicked.connect(self.btnView_Click)
        
        #* 책 챕터 저장
        self.btnSaveToDB.clicked.connect(self.btnSaveToDB_Click)

        # * 이책을 running으로 설정
        self.btnSetRunning.clicked.connect(self.btnSetRunning_Click)

        # * 오늘 작업 상태 조회
        self.btnTodayWork.clicked.connect(self.btnTodayWork_Click)

        #

        #* 새 작업 저장
        self.btnStartNewWork.clicked.connect(self.btnStartNewWork_Click)


        

        #* 01. 크롬 열기
        self.btnLoadChrome.clicked.connect(self.btnLoadChrome_Click)

        #* 02. doWork
        self.btnDoWork.clicked.connect(self.btnDoWork_Click)

        #* 03. 이미지 변경

        self.btnChangeImg.clicked.connect(self.btnChangeImg_Click)

        self.pushButton.clicked.connect(self.pushButton_Click)

    def pushButton_Click(self):
        self.f_change_image()


        zz = 9

    def initUI(self):
        self.setWindowTitle('MyYoutube')

        self.setMinimumSize(200, 200)

        self.tblFiles.setColumnCount(7)
        self.tblFiles.setHorizontalHeaderLabels(["link", "제목", "저자", "추천", "Written_dt", "Saved_dt", "대상여부"])

        self.progressBar_1.reset()
        self.progressBar_2.reset()


    def send_to_clipboard(self, clip_type, data):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(clip_type, data)
        win32clipboard.CloseClipboard()

    # src_unquoted : 인코딩 제거 url
    # src_origin : html 문서에 있는 img src
    def put_img_to_clipboard(self, src_unquoted, src_origin):
        fname = src_unquoted.split("/")[-1]
        fext = fname.split(".")[-1]
        full_fname = "d:/imgs/" + fname

        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent',
                              'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]

        urllib.request.install_opener(opener)
        data = urllib.request.urlretrieve(src_origin, full_fname)

        time.sleep(1)

        image = Image.open(full_fname)

        output = BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()

        self.send_to_clipboard(win32clipboard.CF_DIB, data)

    #* 이미지 엘리먼트를 찾는다.
    def f_get_img_element(self, strSrc):
        imgs = self.driver.find_elements_by_tag_name("img")
        cnt = 0

        elem = None

        for img in imgs:
            nowSrc = img.get_attribute('src')
            if nowSrc == strSrc:
                elem = img
                break

        #* 이미지를 못찾았다면 인코딩 때문이다. 인코딩을 바꿔서 다시 해보자... 2021.07.07 한글 url 에러 처리버전
        if elem == None:
            for img in imgs:
                nowSrc = img.get_attribute('src')
                nowSrc = urllib.parse.unquote(nowSrc)
                if nowSrc == strSrc:
                    elem = img
                    break


        return elem


    # 이미지를 link에서 내 소유로 변경함
    def f_change_images(self):
        # * 쓴 글은 iframe에 있다.
        # self.driver.switch_to_frame(0)
        self.driver.switch_to.frame(0)

        time.sleep(1)

        # ------------------------------------------------------------------------------
        #* 1. 모든 img 태그를 리스트에 넣는다.
        # ------------------------------------------------------------------------------
        imgs = self.driver.find_elements_by_tag_name("img")
        cnt = 0
        
        
        #------------------------------------------------------------------------------
        #* 2. 처리대상 이미지를 리스트에 넣음.
        # ------------------------------------------------------------------------------
        myList = [] #처리대상 이미지를 넣을 리스트
        for img in imgs:
            strSrc = img.get_attribute('src')
            srcText = urllib.parse.unquote(strSrc)

            # * 이미 tistory에 저장되어 있다. 리스트에 넣지 않는다.
            if srcText.startswith('https://blog.kakaocdn.net') \
               or srcText.startswith('blob:https://hanhonghee'):
                continue

            #처리대상 리스트에 이미지 소스를 append
            myList.append(srcText)

        # ------------------------------------------------------------------------------
        # * 3. 이미지 변경
        # ------------------------------------------------------------------------------
        for strSrc in myList:
            #img 엘리먼트를 다시 찾는다. 이유는 선행작업이 페이지에 영향을 주기 때문이다.
            img = self.f_get_img_element(strSrc)

            #image size가 0이면 continue
            rect = img.size
            if rect['height'] == 0 or rect['width'] == 0:
                continue;

            # 이미지가 있는지 확인
            if img == None:
                msg = f"* 이미치 찾기 실패 {strSrc}"
                QMessageBox.critical(self, '에러', msg, QMessageBox.Yes)
            else:
                # 이미지가 있다. 변경한다.
                self.f_change_image(img)

            cnt += 1



        if cnt == 0:
            # 처리된 건수가 없다면 저장하지 않음. 기본페이지로 단순 이동
            self.driver.get(self.startUrl)
            return



        # 다시 원래 frame으로 이동함....
        self.driver.switch_to.default_content()

        msg = f"* 이미지 변환 작업 종료되었습니다.\n - 총 변환건수 : {cnt}건 "
        # QMessageBox.information(self, '작업 종료', msg, QMessageBox.Yes)

        # ------------------------------------------------------------------------------
        # * 07. 등록 버튼을 찾는다.
        # ------------------------------------------------------------------------------
        post_editor_app = self.driver.find_element_by_css_selector("#post-editor-app")
        my_div = post_editor_app.find_element_by_css_selector(".content-aside")
        my_btn = my_div.find_element_by_tag_name("button")
        my_btn.send_keys(Keys.RETURN)

        time.sleep(0.3)
        # ------------------------------------------------------------------------------
        # * 08. release 버튼을 찾는다.
        # ------------------------------------------------------------------------------
        my_div = self.driver.find_element_by_css_selector(".inner_editor_layer.inner_editor_layer1")
        my_btn = my_div.find_element_by_css_selector(".btn.btn-default")

        my_btn.send_keys(Keys.RETURN)
        time.sleep(0.3)

    # 이미지를 link에서 내 소유로 변경함
    def f_change_image(self, img):
        strSrc = img.get_attribute('src')
        strSrcUnQuoted = urllib.parse.unquote(strSrc)

        time.sleep(0.3)

        # ------------------------------------------------------------------------------
        # * 엘리먼트가 보일때까지 루핑돈다.
        # ------------------------------------------------------------------------------
        bLoop = True
        while bLoop:
            try:

                # 스크롤해서 엘리먼트 보이게 하기
                self.driver.execute_script("arguments[0].scrollIntoView()", img)
                time.sleep(0.3)
                img.click()
                bLoop = False
            except Exception as err:
                pass

        time.sleep(0.3)

        # 이미지 엘리먼트를 삭제한다.
        img.send_keys(Keys.DELETE)
        time.sleep(0.2)

        # 이미지를 다운로드 받아 클립보드에 넣는다.
        self.put_img_to_clipboard(strSrcUnQuoted, strSrc)
        time.sleep(0.2)

        actions = ActionChains(self.driver)
        (actions.key_down(Keys.CONTROL)
         .send_keys('v')
         .key_up(Keys.CONTROL)
         .perform()
         )

        time.sleep(0.7)



    # ------------------------------------------------------------------------------
    # * 03. 이미지 변경
    # ------------------------------------------------------------------------------
    def btnChangeImg_Click(self):

        cnt = 0
        start_time = time.time()

        mylist = []  # 링크 저장용 리스트

        # ------------------------------------------------------------------------------
        # * 1. 선택된 체크박스만 작업함.
        # ------------------------------------------------------------------------------
        html_list = self.driver.find_element_by_css_selector(".list_post.list_post_type2")
        items = html_list.find_elements_by_tag_name("li")
        for item in items:
            myLabel = item.find_element_by_css_selector(".ico_blog.ico_checkbox")
            text = myLabel.text
            text = myLabel.get_attribute("innerHTML")

            if text == "선택 됨":
                # ------------------------------------------------------------------------------
                # * 1. 수정 버튼용 링크를 리스트에 저정
                # ------------------------------------------------------------------------------
                div = item.find_element_by_css_selector(".post_btn")
                a = div.find_element_by_tag_name("a")
                href = a.get_attribute('href')
                txt = a.get_attribute('innerHTML')

                if txt == '수정':
                    mylist.append(href)


        # ------------------------------------------------------------------------------
        # * 2. 체크된 글만 mylist에 있다. 이것만 처리한다.
        # ------------------------------------------------------------------------------
        for href in mylist:
            time.sleep(1.5)

            #해당 페이지로 이동한다.
            self.driver.get(href)
            time.sleep(1.5)

            #해당 페이지 그림을 변경한다.
            self.f_change_images()

            cnt += 1

        # your code
        elapsed_time = time.time() - start_time

        msg = f"""
* 작업 종료
 .- 총 작업 건수 : {cnt}
 .- 총 작업 시간 : {elapsed_time:.2f}
        """

        QMessageBox.information(self, '작업 종료', msg, QMessageBox.Yes)

    # ------------------------------------------------------------------------------
    # * 01. 크롬 열기
    # ------------------------------------------------------------------------------
    def btnLoadChrome_Click(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-extensions')  # 확장 프로그램 구동 정지
        #options.add_argument('--start-maximized')  # 최대 크기 윈도우로 시작

        # options.add_argument('window-size=1200x600') #윈도우 크기 지정
        # options.headless = True    #윈도우가 눈에 보이지 않게 실행

        self.driver = webdriver.Chrome(options=options, executable_path="D:/driver/chromedriver_97.exe")

        self.startUrl = self.txtStartUrl.text()  # 네이버 까페 시작 url. 이 url이 게시판을 구분할 수 있어야 함.
        self.startUrl = "https://hanhonghee.tistory.com/manage/posts"
        self.driver.get(self.startUrl)

        #self.driver.get("https://cafe.naver.com/ca-fe/cafes/30454879/menus/9/articles/write?boardType=L")


        # ------------------------------------------------------------------------------
        # * 01. 카카오로 로그인 선택
        # ------------------------------------------------------------------------------
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.btn_login.link_kakao_id'))
        )

        my_btn = self.driver.find_element_by_css_selector(".btn_login.link_kakao_id")
        my_btn.click()

        # ------------------------------------------------------------------------------
        # * 02. 아이디/패스워드
        # ------------------------------------------------------------------------------
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#id_email_2'))
        )
        my_id = self.driver.find_element_by_css_selector("#id_email_2")
        my_id.send_keys("hanhonghee@naver.com")

        my_pwd = self.driver.find_element_by_css_selector("#id_password_3")
        my_pwd.send_keys("h!an1984")

    # 오늘 작업 처리량을 가져온다.
    def f_get_work_status(self):
        yyyymmdd = datetime.today().strftime("%Y%m%d")
        scrap_cnt = 0

        # 1. db에서 읽어온다.
        cursor = con.cursor()
        sql = """
                select a.book_short_url, a.title, ifnull(b.scrap_cnt, 0) as scrap_cnt
                  from books a left outer join book_scrap b
                    on b.site = 'wikidocs.net'
                   and b.scrap_day = ?
                 where a.saved_status = 'running'
                """
        cursor.execute(sql, (yyyymmdd,))
        row = cursor.fetchone()

        if row == None:
            msg = f"[{yyyymmdd}]일자에 books.saved_status = 'running'인 데이터가 없습니다."
            QMessageBox.information(self, '알림', msg, QMessageBox.Yes)
            return

        book_short_url = row[0]
        title = row[1]

        scrap_cnt = row[2]
        self.scrap_cnt = scrap_cnt


        cursor.close()

        self.txtBookTitle.setText(title)
        self.txtBookShortUrl.setText(book_short_url)
        self.txtScrapCnt.setText(str(scrap_cnt))

    #* book_scrap 테이블에 오늘자 레코드 INSERT
    def btnStartNewWork_Click(self):
        yyyymmdd = datetime.today().strftime("%Y%m%d")
        scrap_cnt = 0

        sql = f"""
                insert into book_scrap (site, scrap_day, scrap_cnt) values('wikidocs.net', ?, 0)
            """
        con.execute(sql, (yyyymmdd, ))
        con.commit()

        msg = f"book_scrap 테이블에 오늘 {yyyymmdd} 행을 insert했습니다."
        QMessageBox.information(self, '알림', msg, QMessageBox.Yes)


    def f_update_book_status(self, book_short_url, status):

        yyyymmdd = datetime.today().strftime("%Y%m%d")
        scrap_cnt = 0

        sql = f"""
                    update books set saved_status = ? where  book_short_url = ?
                """
        con.execute(sql, (status, book_short_url))
        con.commit()

    def f_update_crap_count(self, scrap_cnt):

        yyyymmdd = datetime.today().strftime("%Y%m%d")


        sql = f"""
                    update book_scrap 
                       set scrap_cnt = ? 
                     where site = 'wikidocs.net'
                       and scrap_day = ?
                """
        con.execute(sql, (scrap_cnt, yyyymmdd))
        con.commit()

    #* 이 책을 running으로 설정
    def btnSetRunning_Click(self):
        book_short_url = self.txtBookShortUrl.text()
        self.f_update_book_status(book_short_url, 'running')

    #오늘의 작업 처리량 가져오기
    def btnTodayWork_Click(self):
        self.f_get_work_status()

    def btnDoWork_Click(self):
        strShortUrl = self.txtBookShortUrl.text()

        #작업전에 오늘 작업상태를 가져온다.
        self.f_get_work_status()

        #금일 작업 시작
        self.f_doWork(strShortUrl)



    def f_doWork(self, strShortUrl):


        #1. db에서 읽어온다.
        cursor = con.cursor()
        sql = """
        select b.book_short_url, b.jsno, b.sort_no, 
                '['||a.title || '] ' || b.chapter_title as  title, 
                c.contents || char(13)||char(10) || char(13)||char(10) || '* 자료출처 : https://wikidocs.net' || a.book_short_url 
          from books a, book_chapters b, book_contents c
         where a.book_short_url = ? 
           and b.book_short_url = a.book_short_url
           and length(ifnull(b.save_yn, '')) = 0
           and c.book_short_url = b.book_short_url
           and c.jsno = b.jsno
           
         order by b.sort_no
        """
        cursor.execute(sql, (strShortUrl, ))

        cnt = 0
        start_time = time.time()

        for row in cursor.fetchall():
            #------------------------------------------------------------------------------
            #* 일별 한계 저장 건수 체크
            # ------------------------------------------------------------------------------
            if self.scrap_cnt >= 50:
                msg = f"금일 건수 {self.scrap_cnt} 모두 소진함."
                QMessageBox.information(self, '금일 건수 모두 사용', msg, QMessageBox.Yes)
                break

            book_short_url=row[0]
            jsno=row[1]
            title = row[3]
            cont = row[4]


            pyperclip.copy(cont)

            #* html 클립보드에 내용을 copy
            #PutHtml(cont)

            #* 게시판에 글 등록
            self.f_post(title, cont)

            time.sleep(3)

            sql = f"""
                    update book_chapters 
                       set save_yn='Y' 
                     where book_short_url = ? 
                       and jsno = ? 
                """
            con.execute(sql, (book_short_url, jsno))
            con.commit()

            self.scrap_cnt += 1
            self.f_update_crap_count(self.scrap_cnt)



            time.sleep(3)

            cnt += 1

        #* 모든 챕터를 저장 완료후에만 books.saved_status를 done으로 변경
        if row == None:
            #작업 종료 books.saved_status를 'done'으로 변경한다.
            self.f_update_book_status(strShortUrl, 'done')


        # your code
        elapsed_time = time.time() - start_time

        msg = f"""
* 작업 종료
 .- 총 작업 건수 : {cnt}
 .- 총 작업 시간 : {elapsed_time:.2f}
        """

        QMessageBox.information(self, '작업 종료', msg, QMessageBox.Yes)

    # ------------------------------------------------------------------------------
    # 네이버 까페에 글을 쓴다.
    # ------------------------------------------------------------------------------
    def f_post(self, strTitle, strCont):

        self.startUrl = "https://hanhonghee.tistory.com/manage/newpost/"
        self.driver.get(self.startUrl)


        # ------------------------------------------------------------------------------
        # * 01. HTML 글쓰기 콤보 선택
        # ------------------------------------------------------------------------------
        my_btn = self.driver.find_element_by_css_selector("#mceu_20-open")
        my_btn.click()

        time.sleep(0.3)
        # ------------------------------------------------------------------------------
        # * 02. 콤보 중 세번째 HTML 선택
        # ------------------------------------------------------------------------------
        my_html_combo = self.driver.find_element_by_css_selector("#mceu_34-text")
        
        my_html_combo.click()
        time.sleep(0.3)

        # ------------------------------------------------------------------------------
        # * 04. 페이지가 완전히 로딩될때까지 대기
        # ------------------------------------------------------------------------------
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.html-editor'))
        )

        # ------------------------------------------------------------------------------
        # * 03. 글 내용 쓸곳 click
        # ------------------------------------------------------------------------------
        my_edit_div = self.driver.find_element_by_css_selector(".CodeMirror-lines")
        my_edit_div.click()
        time.sleep(0.3)

        #pyperclip.paste()
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

        # ------------------------------------------------------------------------------
        # * 06. 제목을 넣는다.
        # ------------------------------------------------------------------------------
        my_title_div = self.driver.find_element_by_css_selector(".html-editor")
        my_text_area = my_title_div.find_element_by_css_selector(".textarea_tit")
        my_text_area.send_keys(strTitle)

        # * 5초 대기해야 저장가능하다.
        time.sleep(0.5)




        # ------------------------------------------------------------------------------
        # * 07. 등록 버튼을 찾는다.
        # ------------------------------------------------------------------------------
        post_editor_app = self.driver.find_element_by_css_selector("#post-editor-app")
        my_div = post_editor_app.find_element_by_css_selector(".content-aside")
        my_btn = my_div.find_element_by_tag_name("button")
        my_btn.send_keys(Keys.RETURN)

        time.sleep(0.3)
        # ------------------------------------------------------------------------------
        # * 08. release 버튼을 찾는다.
        # ------------------------------------------------------------------------------
        my_div = self.driver.find_element_by_css_selector(".inner_editor_layer.inner_editor_layer1")
        my_btn = my_div.find_element_by_css_selector(".btn.btn-default")

        my_btn.send_keys(Keys.RETURN)


    def btnView_Click(self):

        self.progressBar_1.reset()
        self.progressBar_2.reset()
        self.tblFiles.setRowCount(0)

        self.lblStatus.setText("플레이 리스트 가져오는 중...")
        time.sleep(0.1)

        sell_all = "all"
        #------------------------------------------------------------------------------
        # 1. 책 리스트 가져오기
        #------------------------------------------------------------------------------

        page = self.txtPage.text()
        bookTitle = self.txtBookTitle.text()

        self.lblStatus.setText("총 [{}]개의 페이지에서 추출함...".format(page))

        page = int(page)
        bookIdFilter = self.txtBookShortUrl.text()
        # 39
        # get_book_lists(39, tab=sell_all, bookIdFilter = '/book/536')
        all_book_lists = self.get_book_lists(page, tab=sell_all, kw=bookTitle, bookIdFilter = bookIdFilter)



    def btnSaveToDB_Click(self):

        #상태진행바 초기화
        self.progressBar_1.reset()
        self.progressBar_2.reset()

        cnt = self.tblFiles.rowCount()

        # 상태 진행바
        self.progressBar_1.setRange(0, cnt)
        time.sleep(0.1)

        # ------------------------------------------------------------------------------
        # 2. 책의 목차가져오기
        # ------------------------------------------------------------------------------
        books_chapters = []

        downYn = 'N'
        row = 0
        while True:

            cell = self.tblFiles.item(row, 0)
            book_short_url = cell.text()

            cell = self.tblFiles.item(row, 1)
            book_title = cell.text()


            cell = self.tblFiles.item(row, 6)
            if cell != None:
                downYn = cell.text()

            #다운 대상 혹은 모두 저장 체크박스가 켜져 있는 경우
            if downYn == 'Y' or self.chkSaveAll.isChecked():

                print("------------------------------------------------------------------------------")
                print("*** 책의 목차가져오기 : {} url : {}".format(book_title, book_short_url))
                print("------------------------------------------------------------------------------")

                book_url = g_url + book_short_url
                chapters = self.get_book_chapter(book_url, book_short_url)

                print('**** chapters : ', chapters)
                # book_title, book_url, chapters[book_url, chapters, jsno]

                my_chapters = {'book_title': book_title, 'book_short_url': book_short_url, 'chapters': chapters}
                books_chapters.append(my_chapters)
                print("books_chapters : ", books_chapters)

                #------------------------------------------------------------------------------
                #* 챕터 저장
                # ------------------------------------------------------------------------------
                self.save_book_chapter(my_chapters)

                # ------------------------------------------------------------------------------
                # 책 정보 update
                # ------------------------------------------------------------------------------
                self.save_book_info(row)

                # ------------------------------------------------------------------------------
                #* 책 내용 컨텐츠 저장
                # ------------------------------------------------------------------------------
                self.save_contents(my_chapters)
                
                print(chapters)


            row = row + 1
            # 상태 진행바
            self.progressBar_1.setValue(row)

            if row == cnt:
                break



    def get_book_lists(self, max, tab="sell", sort_type="sell", kw="", bookIdFilter="", book_name=""):

        # 상태 진행바
        self.progressBar_1.setRange(0, max)

        self.tblFiles.setRowCount(0)


        # ------------------------------------------------------------------------------
        # * url 가져오기
        # ------------------------------------------------------------------------------
        self.lblStatus.setText("1. 전체 페이지 리스트 가져오기...")

        book_lists = []
        row = 0

        for cur_page in range(1, max + 1):

            self.lblStatus.setText("[{}] 페이지 탐색중...".format(cur_page))
            self.lblStatus.repaint()
            self.rand_sleep()
            links, book_details = self.get_book_url(tab, cur_page, sort_type, kw)

            print('* [{}]번째 get_book_url()에서 총 {}개 책 가져옴.'.format(cur_page, len(links)))

            self.progressBar_2.reset()
            self.progressBar_2.setRange(0, len(links))
            self.progressBar_2.repaint()


            for i in range(0, len(links)):
                link = links[i]
                book_detail = book_details[i]
                book_detail = book_details[i]

                # 상태 진행바
                self.progressBar_2.setValue(i+1)
                time.sleep(0.1)
                #QApplication.processEvents()

                # 북아이디 판별
                if bookIdFilter != "":
                    if bookIdFilter not in link['href']:
                        continue

                # 책 이름 필터 적용
                if book_name != "":
                    if book_name not in link.text:
                        continue

                print("")
                print("------------------------------------------------------------------------------")
                print("**** 책제목 : ", link.text)
                print("**** link url : ", link['href'])
                author_name = book_detail.find('a', {'class': 'menu_link'})
                print("**** 작자명 : ", author_name.text)
                author_name = author_name.text.strip()

                self.lblStatus.setText("* 제목 [{}], 작자명  [{}]".format(link.text, author_name))

                # ------------------------------------------------------------------------------
                # * 수정일자 처리
                # ------------------------------------------------------------------------------
                mydiv = book_detail.findAll("div")

                written_dt = mydiv[1]
                written_dt = written_dt.text.strip()

                # ------------------------------------------------------------------------------
                # - 2021년 01월 12일
                # ------------------------------------------------------------------------------
                written_dt = written_dt[2:]
                print('**** 수정일 :', written_dt)
                written_dt = datetime.strptime(written_dt, '%Y년 %m월 %d일')
                written_dt = written_dt.strftime('%Y-%m-%d %H:%M:%S.%f')

                # ------------------------------------------------------------------------------
                # 추천
                # ------------------------------------------------------------------------------
                mythumb = book_detail.find('a', {'class': 'btn btn-default btn-xs'})

                p = re.compile('(([0-9]|,)+)')

                mythumb = p.search(mythumb.text.strip())
                mythumb = mythumb[1]
                mythumb = int(mythumb.replace(',', ''))  # 숫자형 변환 위해 ,를 제거

                print("**** 추천수 : ", mythumb)
                print("------------------------------------------------------------------------------")

                # 책제목, 저자, 추천수, link url
                book_lists.append([link['href'], link.text, author_name, mythumb, written_dt])


                # maxRows = self.tblFiles.rowCount() + 1
                # self.tblFiles.setRowCount(maxRows)

                #print("maxRows:", maxRows)
                print("href:", link['href'])
                print("text:", link.text)

                self.tblFiles.setRowCount(row+1)
                self.tblFiles.setItem(row, 0, QTableWidgetItem(link['href']))
                self.tblFiles.setItem(row, 1, QTableWidgetItem(link.text))
                self.tblFiles.setItem(row, 2, QTableWidgetItem(author_name))
                self.tblFiles.setItem(row, 3, QTableWidgetItem(str(mythumb)))
                self.tblFiles.setItem(row, 4, QTableWidgetItem(written_dt))

                saved_dt = self.getSavedDate(link['href'])
                self.tblFiles.setItem(row, 5, QTableWidgetItem(saved_dt))

                if written_dt > saved_dt:
                    self.tblFiles.setItem(row, 6, QTableWidgetItem("Y"))

                #time.sleep(0.1)
                #self.tblFiles.repaint()

                row = row + 1


            self.progressBar_1.setValue(cur_page)

        return book_lists

    # 지정된 행의 데이터를 리스트로 리턴한다.
    def getTableRowData(self, row):

        if row > self.tblFiles.rowCount() :
            return None

        col_cnt = self.tblFiles.columnCount()
        row_data = []
        for col in range(0, col_cnt - 1):
            cell = self.tblFiles.item(row, col)
            data = cell.text()
            row_data.append(data)

        return row_data

    def save_book_info(self, row):
        book = self.getTableRowData(row)

        book_short_url = book[0]
        cur = con.cursor()
        cur.execute('delete from books where book_short_url = ?', (book_short_url,))



        saved_dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        #"link", "제목", "저자", "추천", "Written_dt", "Saved_dt", "대상여부"
        cur.execute(
            'INSERT INTO books(book_short_url, title, author, thumb, written_dt, saved_dt) VALUES(?, ?, ?, ?, ?, ?);',
            (book[0], book[1], book[2], book[3], book[4], saved_dt))

        con.commit()




    def getSavedDate(self, book_short_url):
        # ------------------------------------------------------------------------------
        # 3. 책 리스트 db와 비교
        #   .- 신규는 insert
        #   .- written_dt 다른것은 update
        #   .- 위의 조건에 해당할때만 새로운 리스트에 append
        # ------------------------------------------------------------------------------
        cur = con.cursor()

        cur.execute("select count(1), ifnull(max(saved_dt), '0') From books where book_short_url = ?",
                    (book_short_url,))
        rs = cur.fetchone()
        return rs[1]

    # 책 목차 가져오기
    def get_book_chapter(self, url, book_short_url):
        USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'

        response = requests.get(url, headers={'User-Agent': USER_AGENT})

        bs = BeautifulSoup(response.text, "html.parser")
        response.close()
        chapters = bs.findAll("a", {"class": "list-group-item"})

        chapter_list = []
        p = re.compile('javascript:page\(([0-9]+)\)')
        for chapter in chapters:
            chapter_title = chapter.text.strip()
            js_href = chapter['href']

            js_no = p.search(js_href)
            if js_no != None:
                print(chapter_title, js_href, js_no[1])
                chapter_list.append(
                    {'book_short_url': book_short_url, 'jsno': js_no[1], 'chapter_title': chapter_title})

        return chapter_list

    #책 목차 저장하기
    def save_book_chapter(self, book_chapter):
        # ------------------------------------------------------------------------------
        # 4.2 테이블 book_chapters
        # ------------------------------------------------------------------------------
        # books_chapters.append({'book_title': book_title, 'book_short_url': book_short_url, 'chapters': chapters})
        # 책 목차 저장

        book_short_url = book_chapter['book_short_url']
        cur = con.cursor()
        cur.execute('delete from book_chapters where book_short_url = ?', (book_short_url,))


        for sort_no, chapter in enumerate(book_chapter['chapters']):
            print("****chapter : ", chapter)

            cur.execute(
                'INSERT INTO book_chapters(book_short_url, jsno, sort_no, chapter_title) VALUES(?, ?, ?, ?);',
                (book_short_url, chapter['jsno'], sort_no, chapter['chapter_title'])
            )

        con.commit()

    def rand_sleep(self):
        r = random.uniform(1.0, 3.0)
        time.sleep(r)

    def get_book_url(self, tab="sell", page="1", sort_type="sell", kw=""):
        params = {"page": page, "sort_type": sort_type, "kw": kw}
        add_url = "/tab/" + tab
        full_url = g_url + add_url
        print(full_url)
        response = requests.post(full_url, data=params)

        print("response.status_code : {}".format(response.status_code))

        # print(response.text)
        bs = BeautifulSoup(response.text, "html.parser")
        response.close()

        links = bs.findAll("a", {'class': 'book-subject'})
        book_details = bs.findAll("div", {'class': 'book-detail'})

        return [links, book_details]

    # 책 내용 가져오기
    def get_contents(self, myurl):
        content_list = []
        img_list = []

        try:

            response = requests.get(myurl)

            bs = BeautifulSoup(response.text, "html.parser")
            response.close()
            contents = bs.findAll("div", {"class": "page-content tex2jax_process"})
            written_dt = bs.find("div", {"class": "muted text-right"})
            written_dt = written_dt.text.strip()

            for content in contents:

                imgs = content.findAll("img")

                for img in imgs:
                    img = img.get('src')
                    img = urllib.parse.unquote(img)
                    img_list.append(img)


                #html 태그 빼고 내용만 뽑는다...
                #content = content.text.strip()
                content = repr(content)
                content_list.append(content)

        except Exception as ex:
            content_list.append(ex)
            return False, content_list, None

        return True, content_list, img_list, written_dt


    def save_contents(self, arg):
        book = arg
        chapters = book['chapters']
        chapter = chapters[0]
        book_short_url = chapter['book_short_url']



        book_title = book['book_title']
        self.lblStatus.setText("[{}] Contents 저장중.....".format(book_title))
        time.sleep(0.1)



        # ------------------------------------------------------------------------------
        # 4.3 테이블 book_contents
        # ------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------
        # 3. 책의 내용 가져오기
        # ------------------------------------------------------------------------------

        cur = con.cursor()
        cur.execute('delete from book_contents where book_short_url = ?', (book_short_url,))
        cur.execute('delete from book_imgs     where book_short_url = ?', (book_short_url,))


        bcs = book['chapters']
        contents = []

        # 상태진행바 초기화
        self.progressBar_2.reset()

        cnt = len(bcs)

        # 상태 진행바
        self.progressBar_2.setRange(0, cnt)

        for no, bc in enumerate(bcs):
            chapter_title = bc['chapter_title']
            jsno = bc['jsno']
            bc_url = g_url + '/' + jsno
            print(chapter_title, bc_url)
            self.lblStatus.setText("[{}] - [{}] 저장중...".format(book_title, chapter_title))

            rtn, contents, img_list, written_dt = self.get_contents(bc_url)

            mycontents = {'jsno': jsno, 'book_short_url': book_short_url, 'contents': contents[0]}
            print("----mycontents:", mycontents)
            self.rand_sleep()

            cur = con.cursor()
            saved_dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

            strContent = ''
            if rtn and len(contents) > 0: strContent = contents[0]

            #------------------------------------------------------------------------------
            #* 본문의 내용 저장
            # ------------------------------------------------------------------------------
            cur.execute(
                'INSERT INTO book_contents(book_short_url, jsno, contents, written_dt,saved_dt,run_fail_yn) VALUES(?, ?, ?, ?, ?, ?);',
                (book_short_url, jsno, strContent, written_dt, saved_dt, rtn))

            # ------------------------------------------------------------------------------
            # * 본문 이미지 url
            # ------------------------------------------------------------------------------
            for img_no, img_url in enumerate(img_list):
                cur.execute(
                    'INSERT INTO book_imgs(book_short_url, jsno, img_no, img_url, saved_dt,run_fail_yn) VALUES(?, ?, ?, ?, ?, ?);',
                    (book_short_url, jsno, img_no, img_url, saved_dt, rtn))
            print("총 [{}]개의 이미지 url 저장...".format(len(img_list)))


            con.commit()

            self.progressBar_2.setValue(no)

        self.lblStatus.setText("[{}] Contents 저장 완료.....".format(book_title))
        self.progressBar_2.setValue(cnt)
        time.sleep(0.1)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ex = CMyWikiDocs()
    ex.show()
    sys.exit(app.exec_())

