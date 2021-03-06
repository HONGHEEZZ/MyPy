from PyQt5.QtWidgets import *
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


'''
* 파이썬 ui 참고 자료 - wikidoc
- PyQt5 Tutorial - 파이썬으로 만드는 나만의 GUI 프로그램
- 초보자를 위한 Python GUI 프로그래밍 - PyQt5
- python_ Cheat Sheet
'''


# 책 https://wikidocs.net/book/1
# 책 - 챕터 https://wikidocs.net/2
g_url = 'https://wikidocs.net'



my_dlg = uic.loadUiType("../ui/MyWikiDocs.ui")[0]


con = sqlite3.connect("../books.db")

all_book_lists = []


class CMyWikiDocs(QDialog, my_dlg):
    def __init__(self, parent=None):
        print("parent:", parent)
        super().__init__(parent)
        self.setupUi(self)
        # loadUi("test2",self)

        self.initUI()


        self.txtBookIdFilter.setText("/book/536")

        self.btnView.clicked.connect(self.btnView_Click)
        self.btnDownload.clicked.connect(self.btnDownload_Click)


    def initUI(self):
        self.setWindowTitle('MyYoutube')

        self.setMinimumSize(200, 200)

        self.tblFiles.setColumnCount(7)
        self.tblFiles.setHorizontalHeaderLabels(["link", "제목", "저자", "추천", "Written_dt", "Saved_dt", "대상여부"])

        # self.tblFiles.setColumnWidth(0, 400)
        # self.tblFiles.setColumnWidth(1, 300)



        self.progressBar_1.reset()
        self.progressBar_2.reset()

        # self.tblFiles.rowcount = 1

    def btnView_Click(self):

        self.progressBar_1.reset()
        self.progressBar_2.reset()
        self.tblFiles.setRowCount(0)

        self.lblStatus.setText("플레이 리스트 가져오는 중...")
        time.sleep(0.1)

        sell_all = "all"
        # ------------------------------------------------------------------------------
        # 1. 책 리스트 가져오기
        # ------------------------------------------------------------------------------

        page = self.txtPage.text()

        self.lblStatus.setText("총 [{}]개의 페이지에서 추출함...".format(page))

        page = int(page)
        bookIdFilter = self.txtBookIdFilter.text()
        # 39
        # get_book_lists(39, tab=sell_all, bookIdFilter = '/book/536')
        all_book_lists = self.get_book_lists(page, tab=sell_all, bookIdFilter = bookIdFilter)



    def btnDownload_Click(self):

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
                self.tblFiles.repaint()

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
        response = requests.get(url)

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

