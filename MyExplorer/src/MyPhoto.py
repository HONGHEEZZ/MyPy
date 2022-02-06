import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import PyQt5.QtCore as QtCore
from PyQt5.QtGui import *
from PyQt5 import uic

import time
import math

from PIL import Image, ImageFile
from PIL import ImageFont, ImageDraw
import os
import shutil
import glob
import enum

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re
import datetime
from dateutil import parser

my_dlg = uic.loadUiType("ui/MyPhoto.ui")[0]

CHROME_DRIVER_PATH = "D:/driver/chromedriver_95.exe"


class MY_PHOTO_JOB_TYPE(enum.Enum):
    COPY_BY_DATE = 0
    RESERVED = 1


class MyPhotoThread(QThread):
    finished = pyqtSignal(int)
    progressMsg = pyqtSignal(str)
    progressUI = pyqtSignal(object)

    def __init__(self, MY_PHOTO_JOB_TYPE, search_folder, search_type,
                 OPT_PUT_DATE_YN, OPT_PUT_GPS_YN, OPT_RESIZE_YN, OPT_IF_EXIST_NO_SAVE):
        super().__init__()
        self.MY_PHOTO_JOB_TYPE = MY_PHOTO_JOB_TYPE
        self.search_folder = search_folder
        self.search_type = search_type

        self.needStop = False
        self.driver = None

        self.days = ['월', '화', '수', '목', '금', '토', '일']

        # ------------------------------------------------------------------------------
        # * 사진 옵션
        # ------------------------------------------------------------------------------
        self.OPT_PUT_DATE_YN = OPT_PUT_DATE_YN  # 사진에 찍은 날짜 넣기
        self.OPT_PUT_GPS_YN = OPT_PUT_GPS_YN  # 사진에 gps 넣기...
        self.OPT_RESIZE_YN = OPT_RESIZE_YN  # 사진 크기 조정
        self.OPT_IF_EXIST_NO_SAVE = OPT_IF_EXIST_NO_SAVE  # 타겟에 자료가 있으면 작업안함...


        self.dict_gps = {}  # GPS 캐시
        self.dict_trace = {}


    def doWork(self):
        self.f_copy_photos_by_date(self.search_folder, self.search_type)

        # 일자별 주소를 db에 저장한다.
        self.f_make_db_day_address(self.dict_trace)

    def run(self):

        if self.MY_PHOTO_JOB_TYPE == MY_PHOTO_JOB_TYPE.COPY_BY_DATE:
            cnt_tot = self.f_copy_photos_by_date(self.search_folder, self.search_type)

            self.finished.emit(cnt_tot)  # 총 수행건수 종료시그널...

            # 일자별 주소를 db에 저장한다.
            self.f_make_db_day_address(self.dict_trace)



        elif self.MY_PHOTO_JOB_TYPE == MY_PHOTO_JOB_TYPE.RESERVED:
            pass

    #일자별 주소를 db에 저장한다.
    def f_make_db_day_address(self, dict_trace):
        import sqlite3

        strToday = datetime.datetime.today().strftime("%Y%m%d%H%M%S")
        strTableName = 'pic_day_hour' + strToday


        # DB 생성 (오토 커밋)
        conn = sqlite3.connect("MyPicture.db", isolation_level=None)
        # 커서 획득
        c = conn.cursor()
        # 테이블 생성 (데이터 타입은 TEST, NUMERIC, INTEGER, REAL, BLOB 등)
        c.execute(f"CREATE TABLE IF NOT EXISTS {strTableName} ( \
                    pic_day text,  \
                    pic_hour text,  \
                    address text,  \
                    saved_dt TEXT DEFAULT (datetime('now', 'localtime')), \
                    PRIMARY KEY(pic_day, pic_hour))"
                  )


        my_list = []
        for (day, dict_hour) in dict_trace.items():
            for (hour, address) in dict_hour.items():
                t = (day, hour, address)
                my_list.append(t)

        c.executemany(f"INSERT INTO {strTableName}(pic_day, pic_hour, address) VALUES(?,?,?)", my_list)

        c.close()
        conn.commit()

    # ------------------------------------------------------------------------------
    # * 사진을 일자별로 분류한다.
    # * search_folder : 찾을 폴더
    # * search_type : 찾을 종류 사진/동영상
    # ------------------------------------------------------------------------------
    def f_copy_photos_by_date(self, search_folder, search_type):

        if self.OPT_PUT_GPS_YN:
            self.driver = webdriver.Chrome(CHROME_DRIVER_PATH)
            self.driver.get('https://www.google.com/maps')

        # 에러대응 가로/세로 비율이 안맞는 경우 OS Error 나는 것을 방지하기 위한 옵션.
        ImageFile.LOAD_TRUNCATED_IMAGES = True

        # 단계 2 - 사진을 담을 폴더를 없으면 만든다. 지정된 path에 저장함.
        target_root = "d:/__pic"
        if not os.path.exists(target_root):
            os.makedirs(target_root)

        # 폰트 : 일자 및 장소용
        #font_address = ImageFont.truetype('arial.ttf', 20)

        font_address = ImageFont.truetype('malgun.ttf', 20)

        search_type = search_type.lower()

        cnt_dir = 0
        cnt_files = 0
        cnt_found = 0

        # ------------------------------------------------------------------------------
        # * 찾기 시작. 하위디렉토리 모두 탐색...
        # ------------------------------------------------------------------------------
        for curdir, dirs, files in os.walk(search_folder):
            if self.needStop: break

            self.progressMsg.emit(f"{curdir}")

            cnt_dir += 1

            time.sleep(0.001)
            for fname in files:
                cnt_files += 1
                if self.needStop: break

                self.progressMsg.emit(f"{curdir} {fname}")

                ext = fname[-3:].lower()
                # jpg나 png만 처리...
                if ext == 'jpg' or ext == 'png':
                    target_folder, to_name, address = self.f_copy_photo_by_date(curdir, fname, target_root,
                                                                                font_address)
                    self.progressUI.emit(('File', curdir, fname, target_folder, to_name, address))
                    cnt_found += 1

        # 작업 종료 내용 표시...
        cnt_tot = cnt_dir + cnt_files
        self.progressMsg.emit(f"총 폴더[{cnt_dir}]개, 파일 [{cnt_files}]개 중 [{cnt_found}]개 찾음.")

        return cnt_tot

    def f_copy_file(self, fpicSrcFullPath, fpath2save, blnIfExistSkipSave=True):

        # 이미 있으면 저장하지 않음.
        if blnIfExistSkipSave:
            path, fname = os.path.split(fpath2save)
            fname_only, ext = os.path.splitext(fname)

            search_file = os.path.join(path, fname_only + '*' + ext)
            if glob.glob(search_file):
                # * 이미 있다. 단순 종료
                return True

        # 여기까지 왔다는 것은 없다는 것임.
        shutil.copyfile(fpicSrcFullPath, fpath2save)

    # 타겟파일 기 존재여부 확인.
    def f_file_exist_like(self, fpath2save):

        path, fname = os.path.split(fpath2save)
        fname_only, ext = os.path.splitext(fname)

        search_file = os.path.join(path, fname_only + '*' + ext)
        if glob.glob(search_file):
            # * 이미 있다. 단순 종료
            return True

        return False

    def f_get_pic_day(self, fname, exif_data):

        fname1, _ = os.path.splitext(fname)
        pic_day = '__no__date'
        pic_time = ''
        # 메타정보가 없는 경우 파일명에서 일자 추출...
        if exif_data == None or (36867 in exif_data) == False:

            if not fname1.isnumeric():
                pic_day = '__no__date'

            # uinx timestamp임. 1502677785 953
            elif len(fname1) == 10 + 3:

                str = fname1[:10]
                uts = int(str)
                pic_day = datetime.datetime.fromtimestamp(uts).strftime('%Y-%m-%d')
                pic_time = datetime.datetime.fromtimestamp(uts).strftime('%H:%M:%S')

            # 8자리고 20으로 시작하면 파일명이 찍은 날짜다....
            elif len(fname1) == 8 and fname1[:2] == '20':
                pic_day = fname1[:4] + '-' + fname1[4:6] + '-' + fname1[-2:]

        else:
            tm = exif_data[36867]
            pic_day = tm.split()[0].replace(':', '-')
            pic_time = tm.split()[1]

        if pic_day != '__no__date':
            mydt = parser.parse(pic_day)
            a = mydt.weekday()
            pic_day = pic_day + "(" + self.days[a] + ")"

        return pic_day, pic_time

    # ------------------------------------------------------------------------------
    # * 일자 기준 사진 파일 복사....
    # ------------------------------------------------------------------------------
    def f_copy_photo_by_date(self, curdir, fname, target_folder, font_address):

        fname_org = fname

        if fname == 'IMG_1255.JPG':
            zzz = 9
        # 비정상 사진. 아무 처리 하지 않고 사진만 복사한다.
        abnormal_photo = False

        address = ''

        fpicSrcFullPath = os.path.join(curdir, fname)
        cur_cnt = 0
        cnt = 0

        # ------------------------------------------------------------------------------
        # * 사진 찍은 날짜와 시간뽑기...
        # ------------------------------------------------------------------------------
        pic_day = '__no__date'
        pic_time = ''

        # 단계 2 - exif 정보를 읽는다.
        img = exif_data = None
        try:
            img = Image.open(fpicSrcFullPath)
            exif_data = img._getexif()
        except:
            # * 비정상 사진이면 단순 COPY 후 종료
            abnormal_photo = True

        pic_day, pic_time = self.f_get_pic_day(fname, exif_data)

        # 타겟 폴더명 생성, 타겟 폴더 없으면 만든다.
        folder2save, fpath2save = self.f_make_folder_path(target_folder, fname, pic_day)

        # 비정상 사진이면 단순 카피하고 끝냄....
        if abnormal_photo or exif_data == None:

            # 파일명에서 뽑아낸 날짜를 사진에 찍는다.
            if pic_day != '__no__date':

                if self.OPT_RESIZE_YN: self.f_resize_img(img)

                pic_date_time = pic_day + ' ' + pic_time
                spot_text_x = self.f_write_dt(img, font_address, pic_date_time)
                img.save(fpath2save)
                return folder2save, fname, address
            else:
                # 파일 단순 복사....
                self.f_copy_file(fpicSrcFullPath, fpath2save, self.OPT_IF_EXIST_NO_SAVE)
                print("* [abnormal_photo] Target 존재 Skip... --> ", fpath2save)
                return folder2save, fname, address


        elif self.OPT_IF_EXIST_NO_SAVE:
            if self.f_file_exist_like(fpath2save):
                print("* Target 존재 Skip... --> ", fpath2save)
                return folder2save, fname, address

        # * 사진 가로 세로 방향 조정...
        img = self.f_rotate_img(img, exif_data)

        # ------------------------------------------------------------------------------
        # * 사진 크기 조정하기
        # ------------------------------------------------------------------------------
        spot_text_x = 0
        address = 0
        if self.OPT_RESIZE_YN:
            if self.f_resize_img(img) == False: abnormal_photo = True
        if self.OPT_PUT_DATE_YN:
            pic_date_time = pic_day + ' ' + pic_time
            spot_text_x = self.f_write_dt(img, font_address, pic_date_time)
        if self.OPT_PUT_GPS_YN:
            address = self.f_getGPS_text(img, exif_data)
            if address == '': print("* no GPS : ", fname)
            if address != '':
                print("* GPS Exist : ", fname)
                # ------------------------------------------------------------------------------
                # * 파일명 변경 : 장소 추가...
                # ------------------------------------------------------------------------------
                fname_only, ext = os.path.splitext(fname)
                address = ' (' + address + ')'
                fname = fname_only + address + ext

                # 시간 장소별 시간별
                self.f_make_trace(pic_day, pic_time, address)

                # ------------------------------------------------------------------------------
                # * 사진에 장소 찍기...
                # ------------------------------------------------------------------------------
                self.f_write_address(fname, img, address, font_address, spot_text_x)

        # 타겟 폴더명 생성, 타겟 폴더 없으면 만든다.
        folder2save, fpath2save = self.f_make_folder_path(target_folder, fname, pic_day)

        # 단계 6 - 사진을 복사한다. option : image resize....
        if abnormal_photo:
            # 비정상 사진이면 단순 카피하고 끝냄....
            self.f_copy_file(fpicSrcFullPath, fpath2save, self.OPT_IF_EXIST_NO_SAVE)
        else:

            img.save(fpath2save)

        img.close()

        cnt += 1

        return folder2save, fname, address

    # 일자별, 시간별 장소정보를 기록한다.
    def f_make_trace(self, pic_day, pic_time, address):

        hour = pic_time[:2]

        dict_hour = None

        if pic_day in self.dict_trace:
            dict_hour = self.dict_trace[pic_day]

        if dict_hour == None:
            dict_hour = {hour:address}
        else:
            dict_hour[hour]=address

        self.dict_trace[pic_day]=dict_hour

    def f_make_folder_path(self, target_folder, fname, pic_day):

        # 타겟 폴더명 생성
        folder2save = os.path.join(target_folder, pic_day)

        # 저장 안되는 특수 문자 제거
        fname = re.sub('[\/:*?"<>|]', '', fname)
        fpath2save = os.path.join(folder2save, fname)

        # 타겟 폴더 없으면 만든다.
        if not os.path.exists(folder2save): os.makedirs(folder2save)

        return folder2save, fpath2save

    def f_write_address(self, fname, img, address, font_address, spot_text_x):
        # ------------------------------------------------------------------------------
        # * 파일에 장소 쓰기...
        # ------------------------------------------------------------------------------
        draw = ImageDraw.Draw(img)  # Draw 객체를 만든다.
        text_width, text_height = draw.textsize(address, font_address)

        width, height = img.size

        x = spot_text_x - text_width - 10
        y = height - 30
        self.f_draw_text(draw, font_address, address, x, y)

    # * 사진 찍은 방향을 조정(날짜 프린트 위치를 찾기 위해...)
    def f_rotate_img(self, img, exif_data):
        orientation = 0
        if 274 in exif_data: orientation = exif_data[274]

        if orientation == 6:
            img = img.transpose(Image.ROTATE_270)
        elif orientation == 8:
            img = img.transpose(Image.ROTATE_90)

        return img

    def f_resize_img(self, img):
        MAX_WIDTH, MAX_HEIGHT = 1024, 1024
        #MAX_WIDTH, MAX_HEIGHT = 1024*2, 1024*2
        try:
            img.thumbnail((MAX_WIDTH, MAX_HEIGHT))
        except:
            return False
        return True

    # ------------------------------------------------------------------------------
    # * 일자를 사진에 찍는다.
    # ------------------------------------------------------------------------------
    def f_write_dt(self, img, font, pic_day):

        # 이미지가 resize된 이후임. 주의할 것.........
        width, height = img.size

        # 단계 8 글 쓰기
        draw = ImageDraw.Draw(img)  # Draw 객체를 만든다.
        text_width, text_height = draw.textsize(pic_day, font)

        x = width - text_width - 10
        # y = height-text_height-10
        y = height - 30

        # 두껍게
        self.f_draw_text(draw, font, pic_day, x, y)

        spot_text_x = x

        # 글씨의 시작 x 좌표를 리턴한다.
        return spot_text_x

    # 위도 경도를 십진수의 도(degree)로 변환
    # 60초는 1분이고 60분은 1도라는 관계를 이용.
    def f_gps2deg(self, gps):
        d = 1
        deg = 0.0

        den = 1
        # for num, den in gps:
        for num in gps:
            deg += (num / den) / d

            d *= 60

        return deg

    # ------------------------------------------------------------------------------
    # * GPS로 주소 생성
    # ------------------------------------------------------------------------------
    def f_getGPS_text(self, img, exif_data):
        ret = ""

        if exif_data == None: return ret

        if self.driver == None:
            self.driver.get(CHROME_DRIVER_PATH)

        gps_lat = ''
        lat, lon = '', ''
        try:
            from PIL import ExifTags
            gps_k = ExifTags.TAGS
            gps = exif_data[34853]  # gps 데이터
            if gps == None: return ret

            gps_lat = gps[2]  # 위도
            gps_lon = gps[4]  # 경도

            lat = self.f_gps2deg(gps_lat)
            lon = self.f_gps2deg(gps_lon)

            print("* 위도 ", gps_lat, ", ", lat)
            print("* 경도 ", gps_lon, ", ", lon)

        except KeyError:

            pass

        if gps_lat == '': return ret

        # 직접 웹 브라우저에 위치 표시하기
        # import webbrowser
        # url = 'https://www.google.co.kr/maps/place/{},{}'.format(gps_lat, gps_lon)
        # webbrowser.open(url)
        # print(url)

        if lat:
            # ------------------------------------------------------------------------------
            # * 캐시 히트...
            # ------------------------------------------------------------------------------
            if lat in self.dict_gps:
                dict_lat = self.dict_gps[lat]
                if lon in dict_lat:
                    address = dict_lat[lon]
                    print('*********Cash Hit....:', address)
                    return address

            if self.driver == None:
                self.driver = webdriver.Chrome(CHROME_DRIVER_PATH)
                self.driver.get('https://www.google.com/maps')
            elem = self.driver.find_element_by_name("q")
            elem.send_keys(Keys.BACKSPACE * 100)
            elem.send_keys(f"{lat}, {lon}" + Keys.RETURN)
            time.sleep(5)  # 대기시간을 충분히 준다.
            elem = ''
            try:
                elem = self.driver.find_element_by_xpath('//*[@data-section-id]')
            except:
                return ''
            address = elem.text
            print("address : ", address)
            # self.driver.close()

            # 캐시 히트용 딕셔너리에 추가...
            self.dict_gps = {lat: {lon: address}}

            ret = address

        return ret

    def f_draw_text(self, draw, font, text, x, y):

        shadowcolor = 'black'

        # thin border
        draw.text((x - 1, y), text, font=font, fill=shadowcolor)
        draw.text((x + 1, y), text, font=font, fill=shadowcolor)
        draw.text((x, y - 1), text, font=font, fill=shadowcolor)
        draw.text((x, y + 1), text, font=font, fill=shadowcolor)

        # thicker border
        # draw.text((x - 1, y - 1), text, font=font, fill=shadowcolor)
        # draw.text((x + 1, y - 1), text, font=font, fill=shadowcolor)
        # draw.text((x - 1, y + 1), text, font=font, fill=shadowcolor)
        # draw.text((x + 1, y + 1), text, font=font, fill=shadowcolor)

        draw.text((x, y), text, (255, 255, 0), font)

    # 두 gps간 거리....
    def f_dist_between_gps(self, lat1, lon1, lat2, lon2):
        '''
        두 GPS 간 거리 계산
        좌표1 (lat1, lon1)
        좌표2 (lat2, lon2)
        반환값 : meters(float)

        # 서울과 부산역의 직선 거리
        meters = f_dist_between_gps(37.554531, 126.970663, 35.114979, 129.041549)
        print('{:.2f}km'.format(meters/1000))
        ---> 328.60km
        '''

        lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2))
        R = 6371000  # 지구의 반경. 위도에 따라 달라질 수 있음....

        d_lat = lat2 - lat1
        d_lon = lon2 - lon1

        a = (math.sin(d_lat / 2) ** 2) + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c


class MyPhotoUI(QDialog, my_dlg):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setupUi(self)

        self.id = None
        self.password = None

        self.m_checkBox = []

        self.setupUI()

    def setupUI(self):
        # self.setGeometry(1100, 200, 300, 100)
        # self.setWindowTitle("Sign In")
        # self.setWindowIcon(QIcon('icon.png'))

        # 확인해보기를 누르기 전까지는 OK 버튼은 비 활성화
        self.btnOk.setEnabled(False)

        self.tblFiles.setColumnWidth(0, 30)  # 선택
        self.tblFiles.setColumnWidth(1, 60)  # 선택
        self.tblFiles.setColumnWidth(2, 250)  # AS-IS
        self.tblFiles.setColumnWidth(3, 100)  # TO-BE
        self.tblFiles.setColumnWidth(4, 150)  # AS-IS
        self.tblFiles.setColumnWidth(5, 150)  # TO-BE

        self.tblFiles.setSortingEnabled(True)

        # doWork
        self.btnDoWork.clicked.connect(self.btnDoWork_Click)
        self.btnOk.clicked.connect(self.btnOk_Click)

        # Stop 버튼
        self.btnStop.clicked.connect(self.btnStop_Click)

        # 체크박스
        self.chkAll.clicked.connect(self.chkAll_Click)
        self.chkAll.setChecked(True)

        self.txtSearchKey.returnPressed.connect(self.txtSearchKey_returnPressed)

        self.txtSearchKey.setFocus()

        self.cboWork.setCurrentIndex(0)

        # 오른쪽 마우스 클릭
        # 컨텍스트 메뉴
        self.tblFiles.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tblFiles.customContextMenuRequested.connect(self.on_tblFiles_contextMenu)

        self.tblFiles.clicked.connect(self.tblFiles_Clicked)

    def tblFiles_Clicked(self):

        # import matplotlib.image
        # import matplotlib.pyplot

        row = self.tblFiles.currentIndex().row()
        column = self.tblFiles.currentIndex().column()

        if column == 3 or column == 5:
            cell = self.tblFiles.item(row, column)
            fname = cell.text()

            cell = self.tblFiles.item(row, column - 1)
            dir = cell.text()

            fname_full = os.path.join(dir, fname)

            # ndarray = matplotlib.image.imread(fname_full)
            # matplotlib.pyplot.imshow(ndarray)
            # matplotlib.pyplot.show()

            from PIL import Image

            image = Image.open(fname_full)
            image.show()

    def on_tblFiles_contextMenu(self, position):

        it = self.tblFiles.itemAt(position)
        if it is None: return
        r = it.row()
        c = it.column()
        # item_range = QTableWidgetSelectionRange(0, c, self.tblFiles.rowCount() - 1, c)
        # self.tblFiles.setRangeSelected(item_range, True)

        menu = QMenu()

        action_empty = open_folder_action = open_calc = None

        if not self.tblFiles.indexAt(position).isValid():
            action_empty = menu.addAction(self.tr("Empty Area..."))
        else:
            open_folder_action = menu.addAction("Open Folder with Explorer")
            open_calc = menu.addAction("Open Calc")
            open_file = menu.addAction("파일 열기")

        action = menu.exec_(self.tblFiles.viewport().mapToGlobal(position))

        if action == action_empty:
            print("action empty...")

        if action == open_calc:
            from subprocess import Popen
            Popen('calc')

        elif action == open_file:
            dir = self.tblFiles.item(r, 2).text()
            fname = self.tblFiles.item(r, 3).text()
            fpath = os.path.join(dir, fname)

            os.startfile(fpath)

        elif action == open_folder_action:
            print("zzzzzzzzzz")
            item = self.tblFiles.item(r, 2)
            fpath = item.text()

            os.startfile(fpath)

    # ------------------------------------------------------------------------------
    # * 전체 선택 / 해제
    # ------------------------------------------------------------------------------
    def chkAll_Click(self):
        print("******checked.....")
        if len(self.m_checkBox) == 0: return

        value = self.chkAll.isChecked()
        for chk in self.m_checkBox:
            chk.setChecked(value)

    def txtSearchKey_returnPressed(self):
        self.btnDoWork_Click()

    def setUrl(self, fpath):
        self.txtUrl.setText(fpath)
        self.fpath = fpath

    def insertCheckBoxToTable(self):

        self.numRow = self.tblFiles.rowCount()
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
            self.tblFiles.setCellWidget(i, 0, cellWidget)

    def f_addFileAtBottom(self, strDiv, fpath, fname, to_dir, to_name, gps):

        rowPosition = self.tblFiles.rowCount()
        self.tblFiles.insertRow(rowPosition)

        item = QTableWidgetItem(strDiv)

        self.tblFiles.setItem(rowPosition, 1, item)
        self.tblFiles.setItem(rowPosition, 2, QTableWidgetItem(fpath))
        self.tblFiles.setItem(rowPosition, 3, QTableWidgetItem(fname))

        self.tblFiles.setItem(rowPosition, 4, QTableWidgetItem(to_dir))
        self.tblFiles.setItem(rowPosition, 5, QTableWidgetItem(to_name))
        self.tblFiles.setItem(rowPosition, 6, QTableWidgetItem(gps))

        # self.tblFiles.repaint()

        # ------------------------------------------------------------------------------
        # * 새로 추가되는 아이템이 화면에 보이게 처리....
        # ------------------------------------------------------------------------------
        self.tblFiles.scrollToItem(item)
        self.tblFiles.selectRow(rowPosition + 1)

    def f_MyPhotoThread_UI(self, myTuple):

        strDiv = myTuple[0]
        curdir = myTuple[1]
        fname = myTuple[2]

        to_dir = myTuple[3]
        to_name = myTuple[4]
        gps = myTuple[5]

        self.f_addFileAtBottom(strDiv, curdir, fname, to_dir, to_name, gps)

    def f_MyPhotoThread_msg(self, str):

        self.lblMsg.setText(f"{str}")
        # self.lblMsg.repaint()

    def f_MyPhotoThread_finished(self, cnt_tot):
        print('* f_MyPhotoThread_finished *******************')
        self.btnDoWork.setEnabled(True)
        self.btnStop.setEnabled(False)

    def btnStop_Click(self):
        self.MyPhotoThread.needStop = True

    def btnDoWork_Click(self):
        index = self.cboWork.currentIndex()
        self.tblFiles.setRowCount(0)

        # ------------------------------------------------------------------------------
        # * 파일명 찾기
        # ------------------------------------------------------------------------------
        if index == 0:
            search_folder = self.txtUrl.text()
            search_type = self.txtSearchKey.text()

            # ------------------------------------------------------------------------------
            # * 사진 옵션
            # ------------------------------------------------------------------------------
            OPT_PUT_DATE_YN = self.chkDate.isChecked()  # 사진에 찍은 날짜 넣기
            OPT_PUT_GPS_YN = self.chkGPS.isChecked()  # 사진에 gps 넣기...
            OPT_RESIZE_YN = self.chkResize.isChecked()  # 사진 크기 조정
            OPT_IF_EXIST_NO_SAVE = self.chkExistNoSave.isChecked()

            # 쓰레드 인스턴스 생성
            self.MyPhotoThread = MyPhotoThread(MY_PHOTO_JOB_TYPE.COPY_BY_DATE, search_folder, search_type,
                                               OPT_PUT_DATE_YN, OPT_PUT_GPS_YN, OPT_RESIZE_YN, OPT_IF_EXIST_NO_SAVE)

            # 쓰레드 사용 안함. 파이썬은 쓰레드에서 Break Point가 안 잡히는 듯...
            if self.chkUseThread.isChecked() == False:
                self.MyPhotoThread.doWork()

            # 쓰레딩 사용
            if self.chkUseThread.isChecked() == True:
                self.MyPhotoThread.progressMsg.connect(self.f_MyPhotoThread_msg)
                self.MyPhotoThread.progressUI.connect(self.f_MyPhotoThread_UI)
                self.MyPhotoThread.finished.connect(self.f_MyPhotoThread_finished)

                self.MyPhotoThread.start()

                self.btnDoWork.setEnabled(False)
                self.btnStop.setEnabled(True)

    def btnOk_Click(self):
        os.chdir(self.fpath)

        for row, chk in enumerate(self.m_checkBox):
            if chk.isChecked():
                cell = self.tblFiles.item(row, 2)
                file = cell.text()

                cell = self.tblFiles.item(row, 3)
                file2 = cell.text()

                os.rename(file, file2)

                self.close()

        QMessageBox.information(self, '변경 완료', f"* 총 [{row + 1}]건 변경완료")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    dlg = MyPhotoUI()
    dlg.exec_()
