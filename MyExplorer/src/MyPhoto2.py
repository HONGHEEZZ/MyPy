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
import sqlite3

from dataclasses import dataclass #구조체 사용
from . MyCursor import *


# element 로딩완료 대기
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



# img clipboard 처리용
from io import BytesIO
import win32clipboard
from PIL import Image

# ctrl+v용
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip

#unix timestamp를 특정 지역 datetime 변경하기
import pytz

#동영상 찍은 날짜 가져오기
from win32com.propsys import propsys, pscon
GPS_NO_OPLOCK = 0x00000080  # not defined in propsys

my_dlg = uic.loadUiType("ui/MyPhoto2.ui")[0]

CHROME_DRIVER_PATH = "D:/driver/chromedriver_95.exe"
TARGET_ROOT_DIR = r'd:/__pic'

#------------------------------------------------------------------------------
#* 사진 파일 정보 구조체
#------------------------------------------------------------------------------

@dataclass
class CMOVIE_FILE_INFO:
    pic_dir: str = ''
    pic_fname: str = ''
    pic_day: str = ''
    pic_time: str = ''
    pic_day_of_week: str = ''
    pic_width: int = 0
    pic_height: int = 0
    fps: int = 0
    movie_play_time: int = 0
    movie_file_size: int = 0

    pic_dir_adj: str = ''    #저장 폴더
    pic_fname_adj: str = ''  #저장 파일명
    pic_max_seq: int = 0

    pic_uploaded_yn : str = ''
    pic_uploaded_dt : str = ''
    pic_etc1: str = ''
    pic_etc2: str = ''      #18

    def set_record(self, row):
        self.pic_dir = row[0]
        self.pic_fname = row[1]
        self.pic_day = row[2]
        self.pic_time = row[3]
        self.pic_day_of_week = row[4]
        self.pic_width = row[5]
        self.pic_height = row[6]
        self.fpt = row[7]
        self.movie_play_time = row[8]  # 10
        self.movie_file_size = row[9]  # 10
        self.pic_dir_adj = row[10]
        self.pic_fname_adj = row[11]
        self.pic_max_seq = row[12]
        self.pic_uploaded_yn = row[13]
        self.pic_uploaded_dt = row[14]
        self.pic_etc1 = row[15]
        self.pic_etc2 = row[16]


@dataclass
class CFILE_INFO:
    pic_dir: str = ''
    pic_fname: str = ''
    pic_day: str = ''
    pic_time: str = ''
    pic_day_of_week: str = ''
    pic_width: int = 0
    pic_height: int = 0
    pic_gps_yn: str=''
    pic_gps_lat: str=''
    pic_gps_lon: str=''          #10
    pic_dir_adj: str = ''    #저장 폴더
    pic_fname_adj: str = ''  #저장 파일명
    pic_width_adj: int = 0   #저장 이미지 너비
    pic_height_adj: int = 0  #저장 이미지 높이
    pic_uploaded_yn : str = ''
    pic_uploaded_dt : str = ''
    pic_etc1: str = ''
    pic_etc2: str = ''      #18
    pic_address: str = ''      #18

    def set_record(self, row):
        self.pic_dir = row[0]
        self.pic_fname = row[1]
        self.pic_day = row[2]
        self.pic_time = row[3]
        self.pic_day_of_week = row[4]
        self.pic_width = row[5]
        self.pic_height = row[6]
        self.pic_gps_yn = row[7]
        self.pic_gps_lat = row[8]
        self.pic_gps_lon = row[9]  # 10
        self.pic_dir_adj = row[10]
        self.pic_fname_adj = row[11]
        self.pic_width_adj = row[12]
        self.pic_height_adj = row[13]
        self.pic_uploaded_yn = row[14]
        self.pic_uploaded_dt = row[15]
        self.pic_etc1 = row[16]
        self.pic_etc2 = row[17]

        self.pic_address = row[18]  # 유일하게 여기만 pic_address존재함...

#------------------------------------------------------------------------------
#* 사진 관리 매니저 클래스
#------------------------------------------------------------------------------
class CMyPhotoManager(QThread):



    finished = pyqtSignal(int)
    progressMsg = pyqtSignal(str)
    progressUI = pyqtSignal(object)

    processMsgSender = pyqtSignal(str)
    processListSender = pyqtSignal(object)
    processFinSender = pyqtSignal(int)

    def __init__(self, target_root):
        super().__init__()

        self.needStop = False

        self.days = ['월', '화', '수', '목', '금', '토', '일']

        self.target_root = target_root

        self.OPT_PUT_DATE_YN = None  # 사진에 찍은 날짜 넣기
        self.OPT_PUT_GPS_YN = None # 사진에 gps 넣기...
        self.OPT_RESIZE_YN = None # 사진 크기 조정
        self.OPT_IF_EXIST_NO_SAVE = None

        self.job_div = 'f_meta_collect_from_files'
        self.strMediaType = '01.사진'



    def run(self):

        if self.job_div == 'f_meta_collect_from_files':
            self.f_meta_collect_from_files()
        elif self.job_div == 'f_save_pics_to_file':
            self.f_save_pics_to_file()
        elif self.job_div == 'f_meta_collect_Rework':
            self.f_meta_collect_Rework()


    # ----------------------------------------------------------------------------------------------
    # * 여기부터 사용함.
    # ----------------------------------------------------------------------------------------------
    def f_meta_collect_from_files(self):
        # ------------------------------------------------------------------------------
        # * 1. 디렉토리 순회 하며 파일정보를 db에 저장
        # *   .- 촬영시각, 경로, 파일명, width, height, gps
        # ------------------------------------------------------------------------------
        # 여기

        search_folder = self.search_folder


        cnt = 0

        # 테이블을 만든다.
        self.f_make_table()

        # ------------------------------------------------------------------------------
        # * 찾기 시작. 하위디렉토리 모두 탐색...
        # ------------------------------------------------------------------------------
        for curdir, dirs, files in os.walk(search_folder):
            self.processMsgSender.emit(f"{curdir}")

            for fname in files:

                #중지 요청을 받으면 즉시 중지
                if self.needStop:
                    self.processMsgSender.emit(f"* 사용자 취소 요청으로 작업 중지함....[{cnt}]건 처리완료")
                    self.processFinSender.emit(cnt)
                    return

                self.processMsgSender.emit(f"{curdir} {fname}")



                ext = fname[-3:].lower()
                ext = ext.lower()
                print("*** 작업시작:", curdir, fname)
                # jpg나 png만 처리...

                if self.strMediaType == '01.사진' and (ext == 'jpg' or ext == 'png'):
                    file_info = self.f_get_photo_meta(curdir, fname)

                    # UI 리스트 추가용 Signal 전송
                    self.processListSender.emit(file_info)

                    self.f_save_pic_file_info(file_info)

                    cnt += 1
                elif self.strMediaType == '02.동영상' and (ext == 'mp4' or ext == 'mov' or ext == 'avi'):
                    file_info = self.f_get_movie_meta(curdir, fname)

                    # UI 리스트 추가용 Signal 전송
                    self.processListSender.emit(file_info)

                    self.f_save_movie_file_info(file_info, True)

        self.processMsgSender.emit(f"총 [{cnt}] 파일 작업 완료....")


        self.processMsgSender.emit(f"5. 작업 종료...")

        self.processFinSender.emit(cnt)


    # ----------------------------------------------------------------------------------------------
    # * 재작업 처리
    # ----------------------------------------------------------------------------------------------
    def f_meta_collect_Rework(self):

        #video update 구문...
        str = """
            [20190324_120701_816.mp4]

                UPDATE movie_dir_files
                SET
                 pic_day =
                 substr(pic_fname, 1, 4) || '-' || substr(pic_fname, 5, 2) || '-' || substr(pic_fname, 7, 2),

                pic_time =
                       substr(pic_fname, 10, 2) || ':' ||  substr(pic_fname, 12, 2)|| ':' || substr(pic_fname, 14, 2),

                where pic_day = '__no__date'
                and pic_fname like '20%'
                and length(trim(pic_fname)) > 20
                and pic_fname not like '%일반%'

                ;

                [kakaotalk_1498831607117.mp4]
                UPDATE
                movie_dir_files
                SET
                 pic_day =
                 STRFTIME('%Y-%m-%d',
                        datetime(substr(pic_fname, 11, 13) /1000, 'unixepoch')
                       )
                       ,
                pic_time =
                       STRFTIME('%H:%M:%S',
                        datetime(substr(pic_fname, 11, 13) /1000, 'unixepoch')
                       )

                where pic_day = '__no__date'

                and pic_fname like 'kaka%'

                ;

                [2021_01_21 15_07.mp4]

                 update movie_dir_files
                 set pic_day =
                 replace(substr( pic_fname, 1, 10), '_', '-')
                        ,
                pic_time =		replace(substr( pic_fname, 12, 5), '_', ':') || ':00'


                where pic_day = '__no__date'
                and pic_fname like '20%'
                and length(trim(pic_fname)) = 20

                ;
       """





        # ------------------------------------------------------------------------------
        # * __no__date 자료를 다시 분류한다. 메타부터 다시 생성한다.
        # ------------------------------------------------------------------------------
        # 여기

        # DB 생성 (오토 커밋)
        conn = sqlite3.connect("MyPicture.db", isolation_level=None)
        cursor = conn.cursor()

        # 조회 쿼리문 가져오기
        sql = """
                        select pic_dir, pic_fname 
                          from pic_dir_files
                        where pic_day = '__no__date'
                          and ( pic_fname like 'Screenshot%' or pic_fname like '20%')
                    """

        cursor.execute(sql)
        rslt = cursor.fetchall()

        cnt = 0
        numrows = len(rslt)

        rework_files=[]
        for row in range(numrows):
            rs = rslt[row]
            curdir = rs[0]

            fname = rs[1]

            rework_files.append([curdir, fname])

        cursor.close()


        # ------------------------------------------------------------------------------
        # * 재작업 시작
        # ------------------------------------------------------------------------------
        for file in rework_files:

            curdir = file[0]
            self.processMsgSender.emit(f"{curdir}")

            fname = file[1]

            # 중지 요청을 받으면 즉시 중지
            if self.needStop:
                self.processMsgSender.emit(f"* 사용자 취소 요청으로 작업 중지함....[{cnt}]건 처리완료")
                self.processFinSender.emit(cnt)
                return

            self.processMsgSender.emit(f"{curdir} {fname}")

            ext = fname[-3:].lower()
            print("*** 작업시작:", curdir, fname)
            # jpg나 png만 처리...
            if ext == 'jpg' or ext == 'png':
                file_info = self.f_get_photo_meta(curdir, fname)

                # UI 리스트 추가용 Signal 전송
                self.processListSender.emit(file_info)

                self.f_save_meta_file_info(file_info, True)

                cnt += 1

        self.processMsgSender.emit(f"총 [{cnt}] 파일 작업 완료....")

        self.processMsgSender.emit(f"5. 작업 종료...")

        self.processFinSender.emit(cnt)


    #사진 메타 정보를 db에 저장
    def f_save_pic_file_info(self, file_info, ReplaceYn = False):


        # DB 생성 (오토 커밋)
        conn = sqlite3.connect("MyPicture.db", isolation_level=None)
        # 커서 획득
        cursor = conn.cursor()

        #있는 지 확인

        sql = """
                select count(1) as cnt
                  from pic_dir_files
                where pic_dir = ?
                  and pic_fname = ? 
            """
        cursor.execute(sql, (file_info.pic_dir, file_info.pic_name))
        row = cursor.fetchone()

        #있으면 그냥 종료면 아무 처리 하지 않는다.
        if ReplaceYn == False and row[0] > 0:
            return

        # 있으면 Update
        if ReplaceYn == True and row[0] > 0:
            sql = """
                    delete
                      from pic_dir_files
                    where pic_dir = ?
                      and pic_fname = ? 
                """
            cursor.execute(sql, (file_info.pic_dir, file_info.pic_name))

        #------------------------------------------------------------------------------
        # * insert
        # ------------------------------------------------------------------------------
        sql = """ INSERT INTO pic_dir_files(
                            pic_dir , 
                            pic_fname , 
                            pic_day ,
                            pic_time ,
                            pic_day_of_week, 
                            pic_width ,
                            pic_height ,
                            pic_gps_yn,
                            pic_gps_lat,
                            pic_gps_lon, --#10
                            'pic_dir_adj',
                            'pic_fname_adj',
                            'pic_width_adj',
                            'pic_height_adj',
                            'pic_uploaded_yn',
                            'pic_uploaded_dt',
                            'pic_etc1',
                            'pic_etc2'      --#18
                        )
                        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

        tup = ( file_info.pic_dir ,
                file_info.pic_fname ,
                file_info.pic_day ,
                file_info.pic_time ,
                file_info.pic_day_of_week,
                file_info.pic_width ,
                file_info.pic_height ,
                file_info.pic_gps_yn,
                file_info.pic_gps_lat,
                file_info.pic_gps_lon,
                file_info.pic_dir_adj,
                file_info.pic_fname_adj,
                file_info.pic_width_adj,
                file_info.pic_height_adj,
                file_info.pic_uploaded_yn,
                file_info.pic_uploaded_dt,
                file_info.pic_etc1,
                file_info.pic_etc2)
        cursor.execute(sql, tup)

        cursor.close()
        conn.commit()

        # 일자별 주소를 db에 저장한다.

    # 사진 메타 정보를 db에 저장
    def f_save_movie_file_info(self, file_info, ReplaceYn=False):

        # DB 생성 (오토 커밋)
        conn = sqlite3.connect("MyPicture.db", isolation_level=None)
        # 커서 획득
        cursor = conn.cursor()

        # 있는 지 확인

        sql = """
                select count(1) as cnt
                  from movie_dir_files
                where pic_dir = ?
                  and pic_fname = ? 
            """
        cursor.execute(sql, (file_info.pic_dir, file_info.pic_fname))
        row = cursor.fetchone()

        # 있으면 그냥 종료면 아무 처리 하지 않는다.
        if ReplaceYn == False and row[0] > 0:
            return

        # 있으면 Update
        if ReplaceYn == True and row[0] > 0:
            sql = """
                    delete
                      from movie_dir_files
                    where pic_dir = ?
                      and pic_fname = ? 
                """
            cursor.execute(sql, (file_info.pic_dir, file_info.pic_fname))

        # ------------------------------------------------------------------------------
        # * insert
        # ------------------------------------------------------------------------------
        sql = """ INSERT INTO movie_dir_files(
                            pic_dir , 
                            pic_fname , 
                            pic_day ,
                            pic_time ,
                            pic_day_of_week, 
                            pic_width ,
                            pic_height ,
                            fps, 
                            movie_play_time,
                            movie_file_size,
                            pic_dir_adj,
                            pic_fname_adj, 
                            pic_max_seq,
                            pic_uploaded_yn,
                            pic_uploaded_dt,
                            pic_etc1,
                            pic_etc2      
                        )
                        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

        tup = (file_info.pic_dir,
               file_info.pic_fname,
               file_info.pic_day,
               file_info.pic_time,
               file_info.pic_day_of_week,
               file_info.pic_width,
               file_info.pic_height,

               file_info.fps,
               file_info.movie_play_time,
               file_info.movie_file_size,
               file_info.pic_dir_adj,
               file_info.pic_fname_adj,
               file_info.pic_max_seq,

               file_info.pic_uploaded_yn,
               file_info.pic_uploaded_dt,
               file_info.pic_etc1,
               file_info.pic_etc2)

        cursor.execute(sql, tup)

        cursor.close()
        conn.commit()

        # 일자별 주소를 db에 저장한다.
    #사진 메타 테이블 생성
    def f_make_table(self):

        strToday = datetime.datetime.today().strftime("%Y%m%d%H%M%S")

        # DB 생성 (오토 커밋)
        conn = sqlite3.connect("MyPicture.db", isolation_level=None)
        # 커서 획득
        c = conn.cursor()
        # 테이블 생성 (데이터 타입은 TEST, NUMERIC, INTEGER, REAL, BLOB 등)
        c.execute(f"CREATE TABLE IF NOT EXISTS pic_dir_files ( \
                            pic_dir text, \
                            pic_fname text, \
                            pic_day text,  \
                            pic_time text,  \
                            pic_day_of_week, \
                            pic_width INTEGER, \
                            pic_height INTEGER, \
                            pic_gps_yn text, \
                            pic_gps_lat text, \
                            pic_gps_lon text, \
                            pic_dir_adj	TEXT,  \
                            pic_fname_adj	TEXT,  \
                            pic_width_adj	INTEGER,  \
                            pic_height_adj	INTEGER, \
                            pic_uploaded_yn TEXT, \
                            pic_uploaded_dt TEXT, \
                            pic_etc1 TEXT, \
                            pic_etc2 TEXT, \
                            saved_dt TEXT DEFAULT (datetime('now', 'localtime')), \
                            PRIMARY KEY(pic_dir, pic_fname))"
                  )

    # ------------------------------------------------------------------------------
    # * 동영상 메타 정보
    # ------------------------------------------------------------------------------
    def f_get_movie_meta(self, curdir, fname):

        file_info = CMOVIE_FILE_INFO()
        file_info.pic_dir = curdir
        file_info.pic_fname = fname

        # 비정상 사진. 아무 처리 하지 않고 사진만 복사한다.
        abnormal_photo = False

        fullpath = os.path.join(curdir, fname)

        fullpath = fullpath.replace('/', '\\')
        # ------------------------------------------------------------------------------
        # * 1. 사진 찍은 날짜와 시간뽑기...
        # ------------------------------------------------------------------------------
        pic_day = '__no__date'
        pic_time = ''

        # 단계 2 - exif 정보를 읽는다.
        img = exif_data = None
        try:


            properties = propsys.SHGetPropertyStoreFromParsingName(fullpath, None, GPS_NO_OPLOCK,
                                                                   propsys.IID_IPropertyStore)
            dt = properties.GetValue(pscon.PKEY_Media_DateEncoded).GetValue()
            if dt:
                KST = pytz.timezone('Asia/Seoul')
                new_dt = dt.astimezone(KST)
                print(new_dt.astimezone().strftime('%Y-%m-%d %H:%M:%S'))
            else:
                ts = os.path.getmtime(fullpath)  # 1507245810.6208477
                dt = datetime.fromtimestamp(ts)

            KST = pytz.timezone('Asia/Seoul')
            new_dt = dt.astimezone(KST)
            print(new_dt.astimezone().strftime('%Y-%m-%d %H:%M:%S'))
            pic_day = new_dt.astimezone().strftime('%Y-%m-%d')
            pic_time = new_dt.astimezone().strftime('%H:%M:%S')
        except Exception as e:
            print('예외가 발생했습니다.', e)
            abnormal_photo = True
            file_info.pic_etc1 = e.args[0]




        # # ------------------------------------------------------------------------------
        # # f_get_pic_day()에서는 주어진 파일명 혹은 exif_data에서 날짜와 시간정보만 추출한다.
        # # abnormal_photo 면 __no__date로 리턴함.
        # # ------------------------------------------------------------------------------
        # pic_day, pic_time = self.f_get_pic_day(fname, exif_data)
        # # pic_day --> __no__date 처리 필요
        #
        # pic_width = img.width
        # pic_height = img.height
        #
        file_info.pic_day = pic_day
        file_info.pic_time = pic_time
        # file_info.pic_width = pic_width
        # file_info.pic_height = pic_height

        #디렉토리 없으면 만들기
        my_dir = f"d:\\movies\\{pic_day}\\"
        if not os.path.exists(my_dir):
            os.makedirs(my_dir)


        if pic_day != '__no__date':
            mydt = parser.parse(pic_day)
            a = mydt.weekday()
            file_info.pic_day_of_week = self.days[a]

        # ------------------------------------------------------------------------------
        # * 사진 play time 구하기
        # ------------------------------------------------------------------------------
        from moviepy.editor import VideoFileClip
        from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

        try:

            file_info.movie_file_size = os.path.getsize(fullpath)

            clip = VideoFileClip(fullpath)
            file_info.fps = clip.fps
            file_info.movie_play_time = clip.duration

            file_info.pic_height = clip.h
            file_info.pic_width = clip.w

            d = int(file_info.movie_play_time)

            # 확장자 제거 파일명만 얻기
            s = os.path.splitext(file_info.pic_fname)
            fname_only = os.path.split(s[0])
            fname_only = fname_only[1]

            index = 0
            step = 30 #기본 step은 30
            #동영상 길이가 30*20보다 크면 조절함, 네이버 까페에는 그림이 20장만 올라간다.
            if (d > 30*20):
                step = d / 19
                step = int(step)

            for i in range(1, d, step):
                index += 1
                seq = str(index)
                seq = seq.zfill(2)

                f = fname_only + "_" + seq + ".jpg"
                #이미 파일이 있으면 에러난다.
                if not os.path.exists(f):
                    clip.save_frame(f"{my_dir}{f}", i)

            file_info.pic_max_seq = index
            file_info.pic_dir_adj = my_dir
            file_info.pic_fname_adj = fname_only + "_xx" + ".jpg" #뒤에서 _xxx를 replace 해서 사용함.


        except Exception as e:
            print('예외가 발생했습니다.', e)

            file_info.pic_etc1 = file_info.pic_etc1 + "; " + e.args[0]


        return file_info

    # ------------------------------------------------------------------------------
    # * 사진 메타 정보
    # ------------------------------------------------------------------------------
    def f_get_photo_meta(self, curdir, fname):

        file_info = CFILE_INFO()
        file_info.pic_dir = curdir
        file_info.pic_fname = fname

        # 비정상 사진. 아무 처리 하지 않고 사진만 복사한다.
        abnormal_photo = False

        fpicSrcFullPath = os.path.join(curdir, fname)

        # ------------------------------------------------------------------------------
        # * 1. 사진 찍은 날짜와 시간뽑기...
        # ------------------------------------------------------------------------------
        pic_day = '__no__date'
        pic_time = ''

        # 단계 2 - exif 정보를 읽는다.
        img = exif_data = None
        try:
            img = Image.open(fpicSrcFullPath)
            exif_data = img._getexif()

            #gps 정보가 있는지 확인
            if exif_data and (34853 in exif_data) and (2 in exif_data[34853]):
                file_info.pic_gps_yn = 'Y'

                gps = exif_data[34853]  # gps 데이터
                # 위도(latitude)와 경도(longitude)
                gps_lat = gps[2]  # 위도
                gps_lon = gps[4]  # 경도

                lat = self.f_gps2deg(gps_lat)
                lon = self.f_gps2deg(gps_lon)

                file_info.pic_gps_lat = lat
                file_info.pic_gps_lon = lon

        except Exception as e:
            print('예외가 발생했습니다.', e)
            abnormal_photo = True
            file_info.pic_etc1 = e.args[0]
            return file_info

        # ------------------------------------------------------------------------------
        # f_get_pic_day()에서는 주어진 파일명 혹은 exif_data에서 날짜와 시간정보만 추출한다.
        # abnormal_photo 면 __no__date로 리턴함.
        # ------------------------------------------------------------------------------
        pic_day, pic_time = self.f_get_pic_day(fname, exif_data)
        # pic_day --> __no__date 처리 필요

        pic_width = img.width
        pic_height = img.height

        file_info.pic_day = pic_day
        file_info.pic_time = pic_time
        file_info.pic_width = pic_width
        file_info.pic_height = pic_height

        if pic_day != '__no__date' and not pic_day.startswith('0'):
            mydt = parser.parse(pic_day)
            a = mydt.weekday()
            file_info.pic_day_of_week = self.days[a]

        img.close()

        return file_info

    #------------------------------------------------------------------------------
    # EXIF에서 날짜와 시간 정보 추출, 없으면 사진 파일명에서 추출
    # ------------------------------------------------------------------------------
    def f_get_pic_day(self, fname, exif_data):

        fname1, _ = os.path.splitext(fname)
        pic_day = '__no__date'
        pic_time = ''

        # 메타정보가 없는 경우 파일명에서 일자 추출...
        if exif_data == None or (36867 in exif_data) == False:

            if fname1.startswith('B612_'):
                fname1 = fname1[5:]


            # 8자리고 20으로 시작하면 파일명이 찍은 날짜다....
            if len(fname1) >= 8 and fname1.startswith('20') and fname1[:8].isdigit():
                pic_day = fname1[:4] + '-' + fname1[4:6] + '-' + fname1[6:8]

            #Screenshot_2015-09-14-22-42-34.png
            #Screenshot_20160917-203614
            elif fname1.startswith('Screenshot_'):
                pic_day = fname1.replace('-', '')

                pic_day = pic_day[11:19]

                pic_day = pic_day[:4] + '-' + pic_day[4:6] + '-' + pic_day[6:8]


            #08_7_9.jpg
            elif fname1.count('_') >= 2:
                split_list = fname1.split('_')

                year = split_list[0]
                month = split_list[1]
                day = split_list[2][:2]

                # 처리 07_10_1(1).jpg
                if not day[1:2].isdigit():
                    day = day[:1]

                #* 년월일이 숫자가 아닌 경우는 날짜가 아님....
                if not ( year.isdigit() and month.isdigit() and day.isdigit() and
                         len(year) <= 4 and len(month) <=2 and len(day) <=2):
                    return pic_day, pic_time


                if len(year) == 2:
                    year = '20' + year
                month = month.zfill(2)
                day = day.zfill(2)

                pic_day = year + '-' + month + '-' + day



            # uinx timestamp임. 1502677785 953
            elif len(fname1) >= 10 and fname1[:10].isdigit():

                str = fname1[:10]
                uts = int(str)

                utc_datetime = datetime.datetime.fromtimestamp(uts)
                seoul_zone = pytz.timezone('Asia/Seoul')
                seoul_datetime = datetime.datetime.fromtimestamp(uts, seoul_zone)

                pic_day = seoul_datetime.strftime('%Y-%m-%d')
                pic_time = seoul_datetime.strftime('%H:%M:%S')



        else:
            tm = exif_data[36867]
            pic_day = tm.split()[0].replace(':', '-')
            pic_time = tm.split()[1]

        return pic_day, pic_time

    # ------------------------------------------------------------------------------
    # 위도 경도를 십진수의 도(degree)로 변환
    # 60초는 1분이고 60분은 1도라는 관계를 이용.
    # ------------------------------------------------------------------------------
    def f_gps2deg(self, gps):
        d = 1
        deg = 0.0

        den = 1
        # for num, den in gps:
        for num in gps:
            deg += (num / den) / d

            d *= 60

        return deg

    def f_save_pics_to_file_query_sql(self):
        sql = """ 
            select 
                    a.pic_dir,
                    a.pic_fname,
                    a.pic_day,
                    a.pic_time,
                    a.pic_day_of_week,
                    a.pic_width,
                    a.pic_height,
                    a.pic_gps_yn, 
                    a.pic_gps_lat,
                    a.pic_gps_lon, --#10
                    IFNULL(b.pic_gps_loc, '') as pic_gps_loc ,

                    a.pic_dir_adj,
                    a.pic_fname_adj,
                    a.pic_width_adj,
                    a.pic_height_adj,

                    a.pic_uploaded_yn,
                    a.pic_uploaded_dt,
    
                    a.pic_etc1,
                    a.pic_etc2	
                from pic_dir_files a left outer join pic_gps b
                  on b.pic_gps_lat = a.pic_gps_lat
                  and b.pic_gps_lon = a.pic_gps_lon
                  
                where length(ifnull(a.pic_fname_adj, '')) = 0 
                
                order by 1,2,3,4
                """
        return sql

    # ------------------------------------------------------------------------------
    #* 사진을 저장한다.
    #  .- 일자별 폴더에 저장
    #  .- 최대 Size 1024
    #  .- 하단에 일자 및 GPS 보기
    # ------------------------------------------------------------------------------
    def f_save_pics_to_file(self):
        myCur = CMyCursor()

        # DB 생성 (오토 커밋)
        conn = sqlite3.connect("MyPicture.db", isolation_level=None)
        cursor = conn.cursor()

        # 조회 쿼리문 가져오기
        sql = self.f_save_pics_to_file_query_sql()

        cursor.execute(sql)
        rslt = cursor.fetchall()


        numcols = len(rslt[0])
        numrows = len(rslt)


        fi = CFILE_INFO()

        # 에러대응 가로/세로 비율이 안맞는 경우 OS Error 나는 것을 방지하기 위한 옵션.
        ImageFile.LOAD_TRUNCATED_IMAGES = True

        objFont = ImageFont.truetype('malgun.ttf', 40)

        cnt = 0
        # Loops to add values into QTableWidget
        for row in range(numrows):
            #RecordSet을 file_info 타입으로 변환
            fi.set_record(rslt[row])

            self.processMsgSender.emit(f"{fi.pic_dir} {fi.pic_fname}")

            #------------------------------------------------------------------------------
            #* 같은 이름으로 받으면 변수 값 갱신이 잘 안됨. 파이썬 버그로 추정된다.
            # ------------------------------------------------------------------------------
            new_fi = self.f_save_pic_to_file(fi, objFont)


            if new_fi.pic_etc2:
                print(f"*** fi.pic_etc2에 값이 있음 : ", new_fi.pic_dir, ": ", new_fi.pic_fname, " : ", new_fi.pic_etc2)
                self.processMsgSender.emit(
                    f"*** fi.pic_etc2에 값이 있음 : {new_fi.pic_dir} : {new_fi.pic_fname} : {new_fi.pic_etc2}")

            # print("* f_save_pics_to_file() : ", fi.pic_dir, ": ", fi.pic_fname, " : ", fi.pic_dir_adj)

            # UI 리스트 추가용 Signal 전송
            self.processListSender.emit(new_fi)

            # print("* emit() 후: ", fi.pic_dir, ": ", fi.pic_fname, " : ", fi.pic_dir_adj)
            self.f_save_pic_db_update(cursor, new_fi)
            cnt += 1


        cursor.close()
        del myCur

        self.processMsgSender.emit(f"총 [{cnt}] 파일 작업 완료....")

        self.processFinSender.emit(cnt)



    def f_save_pic_db_update(self, cursor, fi):
        sql = """
                        update pic_dir_files
                         set pic_dir_adj = ?
                            ,pic_fname_adj = ?
                            ,pic_width_adj = ?
                            ,pic_height_adj = ?
                            ,pic_etc2 = ?
                        where pic_dir = ?
                          and pic_fname = ? 
                    """

        cursor.execute(sql, (fi.pic_dir_adj, fi.pic_fname_adj, fi.pic_width_adj, fi.pic_height_adj, fi.pic_etc2
                            ,fi.pic_dir, fi.pic_fname))

        self.processMsgSender.emit(f"* 파일 [{fi.pic_dir_adj}] [{fi.pic_fname_adj}] update 완료....")

    #------------------------------------------------------------------------------
    #* 사진을 원하는 곳에 복사한다.
    #* .- Rotate, size 조정, 촬열일시 쓰기, GPS 쓰기
    # ------------------------------------------------------------------------------
    def f_save_pic_to_file(self, file_info, objFont):

        file_info.pic_dir_adj = 'No...'
        file_info.pic_width_adj = 0
        file_info.pic_height_adj = 0

        # ------------------------------------------------------------------------------
        # *1. 원번 파일 존재여부 체크
        # ------------------------------------------------------------------------------
        fpicSrcFullPath = os.path.join(file_info.pic_dir, file_info.pic_fname)

        if os.path.exists(fpicSrcFullPath) == False:
            file_info.pic_etc2 = '파일이 존재하지 않습니다.'
            return file_info

        # ------------------------------------------------------------------------------
        # * 2. 목표 파일명 생성
        # ------------------------------------------------------------------------------
        file_info.pic_fname_adj = file_info.pic_fname

        # ------------------------------------------------------------------------------
        # * 2.1 목표 파일명 장소 추가
        # ------------------------------------------------------------------------------
        fname_only, ext = os.path.splitext(file_info.pic_fname_adj)
        address = file_info.pic_address
        if address :
            address = ' (' + file_info.pic_address + ')'
        file_info.pic_fname_adj = fname_only + address + ext

        # ------------------------------------------------------------------------------
        # 2.2 타겟 폴더 생성, 타겟 폴더 없으면 만든다.
        # ------------------------------------------------------------------------------
        folder2save = self.f_make_folder_path(self.target_root, file_info.pic_day)
        file_info.pic_dir_adj = folder2save  # 저장 directory

        # ------------------------------------------------------------------------------
        # * 2.3 저장 안되는 특수 문자 제거
        # ------------------------------------------------------------------------------
        file_info.pic_fname_adj = re.sub('[\/:*?"<>|]', '', file_info.pic_fname_adj)

        # ------------------------------------------------------------------------------
        # * 2.4 목표 파일명 생성
        # ------------------------------------------------------------------------------
        fname2save = os.path.join(self.target_root, file_info.pic_day, file_info.pic_fname_adj)

        # ------------------------------------------------------------------------------
        # * 2.5 이미 있다. return
        # ------------------------------------------------------------------------------
        if os.path.isfile(fname2save) and self.OPT_IF_EXIST_NO_SAVE:
            print(f"* {fname2save} 존재함. 저장하지 않음....")
            return file_info

        # ------------------------------------------------------------------------------
        # *3 - exif 정보를 읽는다.
        # ------------------------------------------------------------------------------
        img = exif_data = None
        try:
            img = Image.open(fpicSrcFullPath)
            exif_data = img._getexif()

        except Exception as e:
            print('예외가 발생했습니다.', e)

            file_info.pic_etc2 = e.args[0]
            abnormal_photo = True
            return file_info

        # ------------------------------------------------------------------------------
        # * 4. 사진 가로 세로 방향 조정...
        # ------------------------------------------------------------------------------
        img = self.f_rotate_img(img, exif_data)


        # ------------------------------------------------------------------------------
        # * 5. 사진 크기 조정하기
        # ------------------------------------------------------------------------------
        x_text_pos = 0
        if self.OPT_RESIZE_YN:
            if self.f_resize_img(img) == False:
                abnormal_photo = True

            file_info.pic_width_adj = img.width
            file_info.pic_height_adj = img.height

        # ------------------------------------------------------------------------------
        # * 6. 사진에 날짜 넣기
        # ------------------------------------------------------------------------------
        if self.OPT_PUT_DATE_YN:
            pic_date_time = f"{file_info.pic_day}({file_info.pic_day_of_week}) {file_info.pic_time}"

            #찍은 날짜가 없어 __no__date인 경우는 파일명을 찍어준다.
            strSignString = pic_date_time
            if strSignString.startswith('__no__date') or strSignString.startswith('0000'):
                strSignString = file_info.pic_fname

            x_text_pos = self.f_write_dt(img, objFont, strSignString)

        # ------------------------------------------------------------------------------
        # * 7. 사진에 장소 넣기
        # ------------------------------------------------------------------------------
        if self.OPT_PUT_GPS_YN and file_info.pic_address != '':
            self.f_write_address(img, file_info.pic_address, objFont, x_text_pos)

        # ------------------------------------------------------------------------------
        # 9. 이미지 저장...
        # ------------------------------------------------------------------------------



        try:
            print('* 저장 직전 [', fname2save, ']')
            img.save(fname2save)
        except Exception as e:
            print('예외가 발생했습니다.', e)

            file_info.pic_etc2 = e.args[0]
            abnormal_photo = True
            return file_info


        img.close()


        return file_info

    def f_make_folder_path(self, target_root, pic_day):

        # 타겟 폴더명 생성
        folder2save = os.path.join(target_root, pic_day)

        # 타겟 폴더 없으면 만든다.
        if not os.path.exists(folder2save): os.makedirs(folder2save)

        return folder2save

    def f_write_address(self, img, address, objFont, x_text_pos):
        # ------------------------------------------------------------------------------
        # * 파일에 장소 쓰기...
        # ------------------------------------------------------------------------------
        draw = ImageDraw.Draw(img)  # Draw 객체를 만든다.
        text_width, text_height = draw.textsize(address, objFont)

        width, height = img.size

        x = x_text_pos - text_width - 10
        y = height - 30
        self.f_draw_text(draw, objFont, address, x, y)

    # * 사진 찍은 방향을 조정(날짜 프린트 위치를 찾기 위해...)
    def f_rotate_img(self, img, exif_data):
        orientation = 0

        # exif_data가 없는 경우 arg 이미지를 그대로 리턴함.
        if exif_data == None:
            return img

        if 274 in exif_data:
            orientation = exif_data[274]

        if orientation == 6:
            img = img.transpose(Image.ROTATE_270)
        elif orientation == 8:
            img = img.transpose(Image.ROTATE_90)

        return img

    def f_resize_img(self, img):
        #MAX_WIDTH, MAX_HEIGHT = 1024, 1024
        MAX_WIDTH, MAX_HEIGHT = 1024*2, 1024*2
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

        x = width - text_width - 20
        # y = height-text_height-10
        y = height - 60

        # 두껍게
        self.f_draw_text(draw, font, pic_day, x, y)

        x_text_pos = x

        # 글씨의 시작 x 좌표를 리턴한다.
        return x_text_pos


    def f_draw_text(self, draw, font, text, x, y):

        shadowcolor = 'black'

        # thin border
        # draw.text((x - 1, y), text, font=font, fill=shadowcolor)
        # draw.text((x + 1, y), text, font=font, fill=shadowcolor)
        # draw.text((x, y - 1), text, font=font, fill=shadowcolor)
        # draw.text((x, y + 1), text, font=font, fill=shadowcolor)

        # thicker border
        draw.text((x - 1, y - 1), text, font=font, fill=shadowcolor)
        draw.text((x + 1, y - 1), text, font=font, fill=shadowcolor)
        draw.text((x - 1, y + 1), text, font=font, fill=shadowcolor)
        draw.text((x + 1, y + 1), text, font=font, fill=shadowcolor)


        draw.text((x, y), text, (255, 255, 0), font)

    # 두 gps간 거리.... 현재는 사용 안함...
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

#------------------------------------------------------------------------------
#* 사진 관리 UI 클래스
#------------------------------------------------------------------------------
class MyPhotoUI2(QDialog, my_dlg):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        #셀레니움 드라이버
        self.driver = None

        #포토 매니저 생성
        self.photoMgr = CMyPhotoManager(TARGET_ROOT_DIR)
        
        #메타 송수신 이벤트 연결
        self.f_metaCollectInit()

        self.setupUi(self)

        self.id = None
        self.password = None

        self.days = ['월', '화', '수', '목', '금', '토', '일']

        self.m_checkBox = []

        self.setupUI()

    def setupUI(self):

        self.cboMediaType.setCurrentText("02.동영상")


        self.txtStartUrl.setText("https://cafe.naver.com/ca-fe/cafes/30454879/menus/51/articles/write?boardType=L")

        # self.setGeometry(1100, 200, 300, 100)
        # self.setWindowTitle("Sign In")
        # self.setWindowIcon(QIcon('icon.png'))

        # 확인해보기를 누르기 전까지는 OK 버튼은 비 활성화
        self.btnOk.setEnabled(False)


        # column header 명 설정.
        lstHeaders = ["dir", "fname", "day", "time", "day_of_week", "width", "height",
                      "gps_yn", "gps_lat", "gps_lon", "address",
                      "dir_adj", "fname_adj", "width_adj", "height_adj",
                      "pic_uploaded_yn", "pic_uploaded_dt", "etc1", "etc2"]

        # row, column 갯수 설정해야만 tablewidget 사용할수있다.
        self.tblFiles.setColumnCount(len(lstHeaders))
        # self.tblFiles.setRowCount(3)

        self.tblFiles.setHorizontalHeaderLabels(lstHeaders)


        self.tblFiles.setColumnWidth(0, 300)  # pic_dir
        self.tblFiles.setColumnWidth(1, 200)  # pic_fname
        self.tblFiles.setColumnWidth(2, 100)  # pic_day
        self.tblFiles.setColumnWidth(3, 100)  # pic_time
        self.tblFiles.setColumnWidth(4, 30)  # pic_day_of_week
        self.tblFiles.setColumnWidth(5, 50)  # pic_width
        self.tblFiles.setColumnWidth(6, 50)  # pic_height

        self.tblFiles.setColumnWidth(7, 30)   # pic_gps_yn
        self.tblFiles.setColumnWidth(8, 170)   # pic_gps_latitude
        self.tblFiles.setColumnWidth(9, 170)   # pic_gps_longitude #10
        self.tblFiles.setColumnWidth(10, 100)  # pic_address

        self.tblFiles.setColumnWidth(11, 200)  # pic_dir_adj
        self.tblFiles.setColumnWidth(12, 200)  # pic_fname_adj
        self.tblFiles.setColumnWidth(13, 50)  # pic_width_adj
        self.tblFiles.setColumnWidth(14, 50)  # pic_height_adj

        self.tblFiles.setColumnWidth(15, 100)  # pic_uploaded_yn
        self.tblFiles.setColumnWidth(16, 100)  # pic_uploaded_dt

        self.tblFiles.setColumnWidth(17, 100)  # pic_etc1
        self.tblFiles.setColumnWidth(18, 100)  # pic_etc2

        self.tblFiles.setSortingEnabled(True)

        # 메타정보 수집
        self.btnGetFileMetaInfo.clicked.connect(self.btnGetFileMetaInfo_Click)

        # 저장된 메타정보 조회
        self.btnQueryMeta.clicked.connect(self.btnQueryMeta_Click)
        
        # GPS 테이블에 데이터 입력
        self.btnMakeGPSGroup.clicked.connect(self.btnMakeGPSGroup_Click)

        # gps 주소 정보 얻어서 저장하기
        self.btnGetAddress.clicked.connect(self.btnGetAddress_Click)

        # 그림파일 저장하기
        self.btnSavePictures.clicked.connect(self.btnSavePictures_Click)

        # 크롬 열기
        self.btnOpenChrome.clicked.connect(self.btnOpenChrome_Click)

        # 까페에 사진 올리기
        self.btnUploadPictures.clicked.connect(self.btnUploadPictures_Click)

        # NoDate 재작업
        self.btnNodateReWork.clicked.connect(self.btnNodateReWork_Click)
        
        



        # Stop 버튼
        self.btnStop.clicked.connect(self.btnStop_Click)



        # doWork
        self.btnDoWork.clicked.connect(self.btnDoWork_Click)
        self.btnOk.clicked.connect(self.btnOk_Click)



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

    def btnStop_Click(self):
        self.photoMgr.needStop = True

    def f_upload_get_min_dt(self, cursor):
        # ------------------------------------------------------------------------------
        # * 1. 가장 오래된 날짜를 먼저 가져온다.
        # ------------------------------------------------------------------------------
        sql = """
                    select min(pic_day) as pic_day
                      From pic_dir_files
                     where ifnull(pic_uploaded_yn, '') = ''
                       and pic_fname_adj is not null
                       and ifnull(pic_day, '') <> ''
                    order by pic_dir_adj, pic_fname_adj
                """
        cursor.execute(sql)
        row = cursor.fetchone()

        if len(row) == 0:
            return None

        pic_day = row[0]

        return pic_day


    def f_upload_get_min_dt_movie(self, cursor):
        # ------------------------------------------------------------------------------
        # * 1. 가장 오래된 날짜를 먼저 가져온다.
        # ------------------------------------------------------------------------------
        sql = """
                    select min(pic_day) as pic_day
                      From movie_dir_files
                     where ifnull(pic_uploaded_yn, '') = ''
                       and pic_fname_adj is not null
                       and ifnull(pic_day, '') <> ''
                    order by pic_dir_adj, pic_fname_adj
                """
        cursor.execute(sql)
        row = cursor.fetchone()

        if len(row) == 0:
            return None

        pic_day = row[0]

        return pic_day


    def f_ncafe_get_bbs_id(self, cursor, pic_day):
        # ------------------------------------------------------------------------------
        # * 1. bbs id를 가져온다.
        #     .- 기본 : 년도별
        #     .- 여행 : 특별 bbs
        # ------------------------------------------------------------------------------
        sql = """ 
                 select  case when b.pic_loc is not null then b.pic_loc  
                        when a.pic_year is not null then a.pic_year
                        else 'zzzz'
                   end as div
                   ,
                   case when b.pic_loc is not null then b.bbs_id
                       when a.pic_year is not null then a.bbs_id
                       else 'https://cafe.naver.com/ca-fe/cafes/30454879/menus/60/articles/write?boardType=L'
                   end as bbs_id
                  
           from pic_year_bbs a 
                left outer join pic_trip_bbs b on b.pic_day = ?
              where a.pic_year =  substr(?, 1, 4)
                        """
        cursor.execute(sql, (pic_day, pic_day))
        row = cursor.fetchone()

        if row == None:

            if pic_day.startswith('20'):
                QMessageBox.information(self, '설정오류',
                                        f"* {pic_day} row == None")
                return None
            else:
                #nodate url
                return 'https://cafe.naver.com/ca-fe/cafes/30454879/menus/60/articles/write?boardType=L'

        if cursor.rowcount == 0:
            QMessageBox.information(self, '설정오류',
                                    f"* {pic_day} 처리 메뉴를 네이버 까페에 만들어야 함....")

        return row[1]

    def f_ncafe_get_bbs_id_movie(self, cursor, pic_day):


        # ------------------------------------------------------------------------------
        # * 1. bbs id를 가져온다.
        #     .- 기본 : 년도별
        #     .- 여행 : 특별 bbs
        # ------------------------------------------------------------------------------
        sql = """ 
                 select  case when b.pic_loc is not null then b.pic_loc  
                        when a.pic_year is not null then a.pic_year
                        else 'zzzz'
                   end as div
                   ,
                   case when b.pic_loc is not null then b.bbs_id
                       when a.pic_year is not null then a.bbs_id
                       else 'https://cafe.naver.com/ca-fe/cafes/30454879/menus/80/articles/write?boardType=L'
                   end as bbs_id

           from movie_year_bbs a 
                left outer join movie_trip_bbs b on b.pic_day = ?
              where a.pic_year =  substr(?, 1, 4)
                        """
        cursor.execute(sql, (pic_day, pic_day))
        row = cursor.fetchone()

        if row == None:

            if pic_day.startswith('20'):
                QMessageBox.information(self, '설정오류',
                                        f"* {pic_day} row == None")
                return None
            else:
                # nodate url
                return 'https://cafe.naver.com/ca-fe/cafes/30454879/menus/80/articles/write?boardType=L'

        if cursor.rowcount == 0:
            QMessageBox.information(self, '설정오류',
                                    f"* {pic_day} 처리 메뉴를 네이버 까페에 만들어야 함....")

        return row[1]


    def f_ncafe_pic_fetch_one(self, cursor, pic_day):
        # ------------------------------------------------------------------------------
        # * 1. 가장 오래된 날짜를 먼저 가져온다.
        # ------------------------------------------------------------------------------
        sql = """ 
                select a.pic_dir_adj, a.pic_fname_adj, a.pic_day, a.pic_time, a.pic_day_of_week, 
                       ifnull(b.pic_gps_loc, '') as pic_gps_loc
                  From pic_dir_files a left outer join pic_gps b
                    on b.pic_gps_lat = a.pic_gps_lat
                   and b.pic_gps_lon = a.pic_gps_lon
                 where ifnull(a.pic_uploaded_yn, '') = ''
                   and a.pic_fname_adj is not null
                   and a.pic_day = ?
                order by a.pic_day, a.pic_time
                """
        cursor.execute(sql, (pic_day,))
        row = cursor.fetchone()

        return row

    def f_ncafe_pic_fetch_one_movie(self, cursor, pic_day):
        # ------------------------------------------------------------------------------
        # * 1. 가장 오래된 날짜를 먼저 가져온다.
        # ------------------------------------------------------------------------------
        sql = """ 
                select a.pic_dir, a.pic_fname, a.pic_day, a.pic_time, a.pic_day_of_week
                       , substr('00' || a.pic_max_seq, -2, 2) as pic_max_seq
                       , a.pic_dir_adj, a.pic_fname_adj
                       , printf ('%d',(a.movie_play_time) / 60) || '분 ' 
					   || printf ('%d',(a.movie_play_time) % 60) || '초' as play_time
					   , printf ('%d',(a.movie_file_size / 1000 / 1000 ))|| 'MB' as file_size
                  From movie_dir_files a
                    
                 where ifnull(a.pic_uploaded_yn, '') = ''
                   and a.pic_fname_adj is not null
                   and a.pic_day = ?
                order by a.pic_day, a.pic_time
                """
        cursor.execute(sql, (pic_day,))
        row = cursor.fetchone()

        return row

    def f_ncafe_pic_fetch_20(self, cursor, pic_day):
        # ------------------------------------------------------------------------------
        # * 1. 가장 오래된 날짜를 먼저 가져온다.
        # ------------------------------------------------------------------------------
        sql = """ 
                select a.pic_dir_adj, a.pic_fname_adj, a.pic_day, a.pic_time, a.pic_day_of_week, 
                       ifnull(b.pic_gps_loc, '') as pic_gps_loc
                  From pic_dir_files a left outer join pic_gps b
                    on b.pic_gps_lat = a.pic_gps_lat
                   and b.pic_gps_lon = a.pic_gps_lon
                 where ifnull(a.pic_uploaded_yn, '') = ''
                   and a.pic_fname_adj is not null
                   and a.pic_width_adj <> 0  --같은 일자/시간 사진이 여러장 있을 경우 pic_width_adj가 0이 아닌 것만 사진이 있다.
                   and a.pic_day = ?
                order by a.pic_day, a.pic_time
                """
        cursor.execute(sql, (pic_day,))
        row = cursor.fetchmany(20)

        if len(row) == 0:
            return None

        return row

    # 업로드 여부 저장 pic_dir_files.pic_uploaded_yn
    def f_ncafe_update_uploaded_yn(self, cursor, pic_day, pic_time):
        # ------------------------------------------------------------------------------
        # * 1. 가장 오래된 날짜를 먼저 가져온다.
        # ------------------------------------------------------------------------------
        sql = """
                    update pic_dir_files set pic_uploaded_yn = 'Y', 
                           pic_uploaded_dt = datetime('now', 'localtime')
                     where pic_day = ?
                       and pic_time = ?
                    """

        cursor.execute(sql, (pic_day, pic_time))
        print(cursor.rowcount, "건 update됨.", pic_day, "일자 ", pic_time)

    # 업로드 여부 저장 pic_dir_files.pic_uploaded_yn
    def f_ncafe_update_uploaded_yn_movie(self, cursor, pic_day, pic_time):
        # ------------------------------------------------------------------------------
        # * 1. 가장 오래된 날짜를 먼저 가져온다.
        # ------------------------------------------------------------------------------
        sql = """
                    update movie_dir_files set pic_uploaded_yn = 'Y', 
                           pic_uploaded_dt = datetime('now', 'localtime')
                     where pic_day = ?
                       and pic_time = ?
                    """

        cursor.execute(sql, (pic_day, pic_time))
        print(cursor.rowcount, "건 update됨.", pic_day, "일자 ", pic_time)

    def f_put_img_to_clipboard(self, full_fname):
        image = Image.open(full_fname)

        output = BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()


    # ------------------------------------------------------------------------------
    #* 네이버에 사진 올리기
    # ------------------------------------------------------------------------------
    def f_ncafe_upload_picture(self, conn, cursor):
        # ------------------------------------------------------------------------------
        #* 1. Not Uploaded 중 가장 오랜된 날짜 가져오기
        # ------------------------------------------------------------------------------
        pic_day = self.f_upload_get_min_dt(cursor)
        if pic_day == None:
            QMessageBox.information(self, '사진 upload',
                                    f"* Upload 할 사진이 없습니다. pic_dir_files 테이블 pic_uploaded_yn 칼럼 확인할 것...")
            return False

        # ------------------------------------------------------------------------------
        #* 3. upload url은 년도별/ 여행별로 가져온다.
        # ------------------------------------------------------------------------------
        self.startUrl = self.f_ncafe_get_bbs_id(cursor, pic_day)
        self.driver.get(self.startUrl)

        # ------------------------------------------------------------------------------
        # * 2. 해당 날짜의 데이터 1개를 가져온다. 하나씩 가져와야 중복 사진 걸러낼 수 있다.
        # ------------------------------------------------------------------------------
        min_time = max_time = gps_address = ''
        pic_time = pic_day_of_week = pic_gps_loc = ''
        time.sleep(2)
        for index in range(20):

            row = self.f_ncafe_pic_fetch_one(cursor, pic_day)
            if row == None:
                break

            pic_dir = row[0]            #저장된 파일 경로
            pic_fname = row[1]          #저장된 파일명

            pic_day = row[2]            #사진 찍은 날
            pic_time = row[3]           #사진 찍은 시간
            pic_day_of_week = row[4]    #요일
            pic_gps_loc = row[5]        #gps 장소

            # ------------------------------------------------------------------------------
            # * 우선 찍은 시간과 장소를 text로 넣음...
            # ------------------------------------------------------------------------------
            strDay = pic_day + "(" + pic_day_of_week + ") "
            strPicTitle = strDay + pic_time + " " + pic_gps_loc
            strPicTitle = strPicTitle.strip()

            pyperclip.copy(f'{strPicTitle}')
            time.sleep(0.5)
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

            # ------------------------------------------------------------------------------
            # * 이미지를 클립보드에 복사
            # ------------------------------------------------------------------------------
            full_path = os.path.join(pic_dir, pic_fname)
            self.f_put_img_to_clipboard(full_path)
            time.sleep(2)

            # ------------------------------------------------------------------------------
            # * 그림 한장 ctrl+v
            # ------------------------------------------------------------------------------
            self.f_post_ctrlv_pic()
            time.sleep(7)

            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()


            if min_time == '': min_time = pic_time
            if pic_time > max_time: max_time = pic_time
            if pic_gps_loc != '' and gps_address == '': gps_address = pic_gps_loc



            # ------------------------------------------------------------------------------
            # * 3. pic_dir_files테이블 pic_uploaded_yn = 'Y'로 셋팅
            # ------------------------------------------------------------------------------
            self.f_ncafe_update_uploaded_yn(cursor, pic_day, pic_time)

        # 2018-05-06(일) 07:15:15 ~ 21:00:31 북태평양
        strDay = pic_day + "(" + pic_day_of_week + ") "


        strTime = min_time
        if min_time != max_time: #시간이 같다는 것은 해당일자에 남은 사진이 하나만 있다는 것임....
            strTime += " ~ " + max_time

        strTitle = strDay + strTime + " " + gps_address

        strSignString = strTitle
        if strSignString.startswith('__no__date'):
            strSignString = pic_fname

        # ------------------------------------------------------------------------------
        #* 제목 넣기
        # ------------------------------------------------------------------------------
        self.f_post_set_title(strTitle)

        # ------------------------------------------------------------------------------
        #* 저장버튼 클릭하기
        # ------------------------------------------------------------------------------
        self.f_post_save_click()
        time.sleep(7)
        conn.commit()



        return True

    # ------------------------------------------------------------------------------
    # * 동영상 파일 업로드
    # ------------------------------------------------------------------------------
    def f_ncafe_upload_mp4(self, conn, cursor, pic_dir, pic_fame):
        # ------------------------------------------------------------------------------
        # * 01. 동영상 upload 버튼을 찾는다.
        # ------------------------------------------------------------------------------
        my_btn = self.driver.find_element_by_css_selector(".se-video-toolbar-button.se-document-toolbar-basic-button.se-text-icon-toolbar-button")

        # ------------------------------------------------------------------------------
        # * 02. 버튼 클릭
        # ------------------------------------------------------------------------------
        my_btn.send_keys(Keys.RETURN)

        time.sleep(0.5)

        # ------------------------------------------------------------------------------
        # * 02. 동영상 파일 upload 클릭
        # ------------------------------------------------------------------------------
        my_btn = self.driver.find_element_by_css_selector(".nvu_btn_append.nvu_local")
        my_btn.send_keys(Keys.RETURN)

        # ------------------------------------------------------------------------------
        # * 03. 파일 대화상자에 파일과 디렉토리 넣기
        # ------------------------------------------------------------------------------
        time.sleep(1)
        full_path = pic_dir + "\\" + pic_fame

        # ------------------------------------------------------------------------------
        # * 04. 동영상 파일 업로드 파일 대화상자 처리....
        # ------------------------------------------------------------------------------
        self.handle_upload_file_dialog(full_path)

        # ------------------------------------------------------------------------------
        # * 05. 동영상 파일 업로드가 끝날때까지 기다린다.
        # *  .- 최대 10분 대기
        # ------------------------------------------------------------------------------
        WebDriverWait(self.driver, 60 * 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.nvu_img_box img'))
        )

        # ------------------------------------------------------------------------------
        # * 06. 사진 title
        # ------------------------------------------------------------------------------
        my_input_title = self.driver.find_element_by_css_selector("#nvu_inp_tit")
        my_input_title.send_keys(pic_fame)


        # ------------------------------------------------------------------------------
        # * 07. 사진 summary
        # ------------------------------------------------------------------------------
        my_input_summary = self.driver.find_element_by_css_selector("#nvu_inp_summary")
        strSummary = pic_fame + "                             [" + pic_dir + "]"
        my_input_summary.send_keys(strSummary)

        time.sleep(0.5)

        # ------------------------------------------------------------------------------
        #* 08. 완료 버튼
        # ------------------------------------------------------------------------------
        my_btn = self.driver.find_element_by_css_selector(".nvu_btn_submit.nvu_btn_type2")
        my_btn.send_keys(Keys.RETURN)
        

    def handle_upload_file_dialog(self, file_path):
        import win32com.client as comclt
        sleep = 2
        windowsShell = comclt.Dispatch("WScript.Shell")
        #time.sleep(sleep)
        # windowsShell.SendKeys("{TAB}{TAB}{TAB}{TAB}{TAB}")

        pyperclip.copy(f'{file_path}')

        time.sleep(2)
        windowsShell.SendKeys("^v", 0)
        time.sleep(1)
        windowsShell.SendKeys("{ENTER}")

    # ------------------------------------------------------------------------------
    # * 네이버에 동영상 올리기
    # ------------------------------------------------------------------------------
    def f_ncafe_upload_movie(self, conn, cursor):
        # ------------------------------------------------------------------------------
        # * 1. Not Uploaded 중 가장 오랜된 날짜 가져오기%
        # ------------------------------------------------------------------------------
        pic_day = self.f_upload_get_min_dt_movie(cursor)
        if pic_day == None:
            QMessageBox.information(self, '동영상 upload',
                                    f"* Upload 할 동영상이 없습니다. pic_dir_files 테이블 pic_uploaded_yn 칼럼 확인할 것...")
            return False

        # ------------------------------------------------------------------------------
        # * 3. upload url은 년도별/ 여행별로 가져온다.
        # ------------------------------------------------------------------------------
        self.startUrl = self.f_ncafe_get_bbs_id_movie(cursor, pic_day)
        self.driver.get(self.startUrl)


        # ------------------------------------------------------------------------------
        # * 2. 해당 날짜의 동영상 1개를 가져온다. 하나씩 가져와야 중복 사진 걸러낼 수 있다.
        # ------------------------------------------------------------------------------
        min_time = max_time = ''
        pic_time = pic_day_of_week = ''
        time.sleep(2)

        row = self.f_ncafe_pic_fetch_one_movie(cursor, pic_day)
        if row == None:
            return

        pic_dir = row[0]  # 저장된 파일 경로
        pic_fname = row[1]  # 저장된 파일명

        pic_day = row[2]  # 사진 찍은 날
        pic_time = row[3]  # 사진 찍은 시간
        pic_day_of_week = row[4]  # 요일
        pic_max_seq = row[5]

        pic_dir_adj = row[6]
        pic_fname_adj = row[7]

        movie_play_time = row[8]        #동영상 재생 시간
        movie_file_size = row[9]        #동영상 파일 크기

        # ------------------------------------------------------------------------------
        # * 3. 우선 가져온 동영상 파일을 먼저 올린다.
        # ------------------------------------------------------------------------------
        self.f_ncafe_upload_mp4(conn, cursor, pic_dir, pic_fname)

        time.sleep(1)
        for i in range(5):
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()

        max_seq = int(pic_max_seq)
        # ------------------------------------------------------------------------------
        # * 4. 다음으로는 이미지 캡쳐샷을 올린다.
        # ------------------------------------------------------------------------------
        for index in range(0, max_seq):
            strIndex = str(index+1)
            strIndex = strIndex.zfill(2)

            # movie_dir_files테이블의 pic_fname_adj칼럼을 활용함.
            pic_fname = pic_fname_adj.replace('_xx', '_' + strIndex)

            # ------------------------------------------------------------------------------
            # * 우선 찍은 시간과 요일 text로 넣음...
            # ------------------------------------------------------------------------------
            strDay = pic_day + "(" + pic_day_of_week + ") "
            strPicTitle = strDay + pic_time + " " + strIndex + "번째 스틸컷"
            strPicTitle = strPicTitle.strip()

            pyperclip.copy(f'{strPicTitle}')
            time.sleep(0.5)
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

            # ------------------------------------------------------------------------------
            # * 이미지를 클립보드에 복사
            # ------------------------------------------------------------------------------
            full_path = os.path.join(pic_dir_adj, pic_fname)
            self.f_put_img_to_clipboard(full_path)

            # ------------------------------------------------------------------------------
            # * 그림 한장 ctrl+v
            # ------------------------------------------------------------------------------
            self.f_post_ctrlv_pic()

            for i in range(5):
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()

            if min_time == '': min_time = pic_time
            if pic_time > max_time: max_time = pic_time



        # 2018-05-06(일) 07:15:15 ~ 21:00:31 북태평양
        strDay = pic_day + "(" + pic_day_of_week + ") "

        strTime = min_time
        if min_time != max_time:  # 시간이 같다는 것은 해당일자에 남은 사진이 하나만 있다는 것임....
            strTime += " ~ " + max_time

        strTitle = strDay + strTime + ", PlayTime : " + movie_play_time + ", FileSize : " + movie_file_size

        strSignString = strTitle
        if strSignString.startswith('__no__date'):
            strSignString = pic_fname

        # ------------------------------------------------------------------------------
        # * 제목 넣기
        # ------------------------------------------------------------------------------
        self.f_post_set_title(strTitle)

        # ------------------------------------------------------------------------------
        # * 저장버튼 클릭하기
        # ------------------------------------------------------------------------------
        self.f_post_save_click()

        time.sleep(3)

        # ------------------------------------------------------------------------------
        # * 3. pic_dir_files테이블 pic_uploaded_yn = 'Y'로 셋팅
        # ------------------------------------------------------------------------------
        self.f_ncafe_update_uploaded_yn_movie(cursor, pic_day, pic_time)

        conn.commit()

        return True

    def f_post_ctrlv_pic(self):
        # ------------------------------------------------------------------------------
        # * 04. 페이지가 완전히 로딩될때까지 대기
        # ------------------------------------------------------------------------------
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.textarea_input'))
        )

        ActionChains(self.driver).send_keys(Keys.ENTER)
        ActionChains(self.driver).send_keys(Keys.ENTER)
        ActionChains(self.driver).send_keys(Keys.ENTER)


        # * 5초 대기해야 저장가능하다.
        time.sleep(2)

        # ------------------------------------------------------------------------------
        # * 05. 페이지가 열리면 제일먼저 ctrl+v 한다. 내용은 위에서 클립보드에 넣는다.
        # ------------------------------------------------------------------------------
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

        time.sleep(2)

    def f_post_set_title(self, strTitle):
        # ------------------------------------------------------------------------------
        # * 06. 제목을 넣는다.
        # ------------------------------------------------------------------------------
        my_title = self.driver.find_element_by_css_selector(".textarea_input")
        my_title.send_keys(strTitle)

    def f_post_save_click(self):
        # ------------------------------------------------------------------------------
        # * 07. 등록 버튼을 찾는다.
        # ------------------------------------------------------------------------------
        my_div = self.driver.find_element_by_css_selector(".tool_area")
        my_btn = my_div.find_element_by_tag_name('a')

        # ------------------------------------------------------------------------------
        # * 08. 등록 버튼 버튼 클릭
        # ------------------------------------------------------------------------------
        my_btn.send_keys(Keys.RETURN)

    # ------------------------------------------------------------------------------
    # 네이버 까페에 글을 쓴다.
    # ------------------------------------------------------------------------------
    def f_post(self, strTitle):
        # # ------------------------------------------------------------------------------
        # # * 01. 까페 글쓰기 버튼 찾기
        # # ------------------------------------------------------------------------------
        # my_div = self.driver.find_element_by_css_selector(".cafe-write-btn")
        # my_btn = my_div.find_element_by_tag_name('a')
        #
        # # ------------------------------------------------------------------------------
        # # * 02. 까페 글쓰기 버튼 클릭
        # # ------------------------------------------------------------------------------
        # my_btn.send_keys(Keys.RETURN)
        #
        # # ------------------------------------------------------------------------------
        # # * 03. 새로운 페이지로 크롬 이동
        # # ------------------------------------------------------------------------------
        # cnt = len(self.driver.window_handles)
        # self.driver.switch_to.window(self.driver.window_handles[cnt - 1])

        # ------------------------------------------------------------------------------
        # * 04. 페이지가 완전히 로딩될때까지 대기
        # ------------------------------------------------------------------------------
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.textarea_input'))
        )

        # * 5초 대기해야 저장가능하다.
        time.sleep(0.3)

        # ------------------------------------------------------------------------------
        # * 05. 페이지가 열리면 제일먼저 ctrl+v 한다. 내용은 위에서 클립보드에 넣는다.
        # ------------------------------------------------------------------------------
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

        # * 5초 대기해야 저장가능하다.
        time.sleep(0.3)

        # ------------------------------------------------------------------------------
        # * 06. 제목을 넣는다.
        # ------------------------------------------------------------------------------
        my_title = self.driver.find_element_by_css_selector(".textarea_input")
        my_title.send_keys(strTitle)

        time.sleep(1)

        # ------------------------------------------------------------------------------
        # * 07. 등록 버튼을 찾는다.
        # ------------------------------------------------------------------------------
        my_div = self.driver.find_element_by_css_selector(".tool_area")
        my_btn = my_div.find_element_by_tag_name('a')

        # ------------------------------------------------------------------------------
        # * 08. 등록 버튼 버튼 클릭
        # ------------------------------------------------------------------------------
        my_btn.send_keys(Keys.RETURN)

        # # ------------------------------------------------------------------------------
        # # * 08. 원래 창으로 이동...
        # # ------------------------------------------------------------------------------
        # self.driver.close()
        # # 원래 탭으로 이동
        # self.driver.switch_to.window(self.driver.window_handles[0])

    # ------------------------------------------------------------------------------
    # * 까페에 사진 올리기 
    # *  .- 하루에 200개 게시물
    # *  .- 한 게시물에 20개 사진
    # ------------------------------------------------------------------------------
    def btnUploadPictures_Click(self):
        # DB 생성 (오토 커밋)
        conn = sqlite3.connect("MyPicture.db") # auto commit 안함....
        # 커서 획득
        cursor = conn.cursor()

        self.strMediaType = self.cboMediaType.currentText()

        #게시판은 하루에 200개까지 등록 가능
        max_cnt = 150
        for index in range(max_cnt):


            if self.strMediaType == '01.사진':
                rtn = self.f_ncafe_upload_picture(conn, cursor)
            elif self.strMediaType == '02.동영상':
                time.sleep(4)
                rtn = self.f_ncafe_upload_movie(conn, cursor)


            if rtn == False:
                break

        cursor.close()

        QMessageBox.information(self, '작업 종료', f"* 총 [{index}]건을 Naver에 저장 완료함...")



    def btnOpenChrome_Click(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-extensions')  # 확장 프로그램 구동 정지
        options.add_argument('--start-maximized')  # 최대 크기 윈도우로 시작

        # options.add_argument('window-size=1200x600') #윈도우 크기 지정
        # options.headless = True    #윈도우가 눈에 보이지 않게 실행

        self.driver = webdriver.Chrome(options=options, executable_path=CHROME_DRIVER_PATH)


        self.startUrl = self.txtStartUrl.text()  # 네이버 까페 시작 url. 이 url이 게시판을 구분할 수 있어야 함.
        self.driver.get(self.startUrl)

        #self.driver.get("https://cafe.naver.com/graydidrb")

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




    #------------------------------------------------------------------------------
    #* 사진 저장 버튼 클릭
    # ------------------------------------------------------------------------------
    def btnSavePictures_Click(self):

        self.photoMgr.OPT_PUT_DATE_YN = self.chkDate.isChecked()  # 사진에 찍은 날짜 넣기
        self.photoMgr.OPT_PUT_GPS_YN = self.chkGPS.isChecked()  # 사진에 gps 넣기...
        self.photoMgr.OPT_RESIZE_YN = self.chkResize.isChecked()  # 사진 크기 조정
        self.photoMgr.OPT_IF_EXIST_NO_SAVE = self.chkExistNoSave.isChecked()


        #테이블 그리드 초기화
        self.tblFiles.setRowCount(0)

        photoMgr = self.photoMgr

        # ------------------------------------------------------------------------------
        # * run할때 쓰레드 함수를 구분해서 돌려야 한다.
        # ------------------------------------------------------------------------------
        photoMgr.job_div = 'f_save_pics_to_file'

        # ------------------------------------------------------------------------------
        #* thread를 사용하면 break point가 안먹힌다.
        # ------------------------------------------------------------------------------
        if self.chkDebug.isChecked():
            # 디버깅
            photoMgr.f_save_pics_to_file()

        else:
            # 쓰레드 처리. 이러면 디버깅 안됨.
            photoMgr.start()
            self.btnGetFileMetaInfo.setEnabled(False)
            self.btnMakeGPSGroup.setEnabled(False)
            self.btnGetAddress.setEnabled(False)
            self.btnSavePictures.setEnabled(False)
            self.btnStop.setEnabled(True)

    # ------------------------------------------------------------------------------
    # * btnNodateReWork 재작업 버튼 클릭
    # ------------------------------------------------------------------------------
    def btnNodateReWork_Click(self):

        print('* btnGetFileMetaInfo_Click *******************')

        self.tblFiles.setRowCount(0)

        photoMgr = self.photoMgr

        search_folder = self.txtUrl.text()
        photoMgr.search_folder = search_folder

        # * run할때 쓰레드 함수를 구분해서 돌려야 한다.
        photoMgr.job_div = 'f_meta_collect_Rework'
        if self.chkDebug.isChecked():

            photoMgr.f_meta_collect_Rework()
        else:
            # 쓰레드 생성. 이러면 디버깅 안됨.
            photoMgr.start()

            self.btnGetFileMetaInfo.setEnabled(False)
            self.btnMakeGPSGroup.setEnabled(False)
            self.btnGetAddress.setEnabled(False)
            self.btnSavePictures.setEnabled(False)

            self.btnStop.setEnabled(True)



    #주소를 가져와 pic_gps 테이블에 저장 by selenium
    def btnGetAddress_Click(self):
        # DB 생성 (오토 커밋)
        conn = sqlite3.connect("MyPicture.db", isolation_level=None)
        # 커서 획득
        cursor = conn.cursor()

        sql = """ 
        select pic_gps_lat, pic_gps_lon 
          from pic_gps 
         where pic_gps_loc is null 
         order by 1,2
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        cnt = 0

        for row in rows:
            lat = row[0]
            lon = row[1]

            address = self.f_get_gps_location(lat, lon)

            sql = """
                update pic_gps set pic_gps_loc = ?
                where pic_gps_lat = ?
                  and pic_gps_lon = ? 
            """
            cursor.execute(sql, (address, lat, lon))

            print(f"* [{cursor.rowcount}]건 update 성공....")
            cnt += 1

        cursor.close()
        conn.commit()

        QMessageBox.information(self, 'address 완료', f"* 총 [{cnt}]건을 pic_gps.address에 주소 설정 완료...")

    # 셀레니움으로
    def f_get_gps_location(self, lat, lon):
        address = ''
        if self.driver == None:
            self.driver = webdriver.Chrome(CHROME_DRIVER_PATH)
            self.driver.get('https://www.google.com/maps')
        elem = self.driver.find_element_by_name("q")
        elem.send_keys(Keys.BACKSPACE * 100)
        elem.send_keys(f"{lat}, {lon}" + Keys.RETURN)

        time.sleep(3)  # 대기시간을 충분히 준다.
        # ------------------------------------------------------------------------------
        # * 04. 페이지가 완전히 로딩될때까지 대기
        # ------------------------------------------------------------------------------
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@data-section-id]'))
        )


        elem = ''
        try:
            elem = self.driver.find_element_by_xpath('//*[@data-section-id]')
        except:
            return ''
        address = elem.text
        print("address : ", address)

        return address



    # 새로 추가된 gps lat, log를 pic_gps테이블에 insert함.
    # 기존에 있던 위도, 경도는 insert하지 않음.
    def btnMakeGPSGroup_Click(self):

        # DB 생성 (오토 커밋)
        conn = sqlite3.connect("MyPicture.db", isolation_level=None)
        # 커서 획득
        cursor = conn.cursor()

        sql = """ 
                insert into pic_gps(pic_gps_lat,  pic_gps_lon) 

                select pic_gps_lat,  pic_gps_lon
                from (
                        select a.pic_gps_lat, a.pic_gps_lon, IFNULL(b.pic_gps_lat, 'NotExist') val
                          From pic_dir_files a left outer join pic_gps b
                           on  a.pic_gps_lat = b.pic_gps_lat
                           and a.pic_gps_lon = b.pic_gps_lon
                         where a.pic_gps_yn='Y'
                         group by a.pic_gps_lat, a.pic_gps_lon
                )x
                where x.val = 'NotExist'
                        """
        cursor.execute(sql)

        QMessageBox.information(self, 'insert 완료', f"* 총 [{cursor.rowcount}]건을 pic_gps에 insert완료함...")
        

        cursor.close()
        conn.commit()


    # db에서 메타정보 조회
    def btnQueryMeta_Click(self):

        myCur = CMyCursor()

        # DB 생성 (오토 커밋)
        conn = sqlite3.connect("MyPicture.db", isolation_level=None)
        cursor = conn.cursor()

        sql = """ 
                select 
                        a.pic_dir,
                        a.pic_fname,
                        a.pic_day,
                        a.pic_time,
                        a.pic_day_of_week,
                        a.pic_width,
                        a.pic_height,
                        a.pic_gps_yn, 
                        a.pic_gps_lat,
                        a.pic_gps_lon,
                        IFNULL(b.pic_gps_loc, '') as pic_gps_loc ,
                        
                        a.pic_dir_adj, 
                        a.pic_fname_adj, 
                        a.pic_width_adj, 
                        a.pic_height_adj, 
                        a.pic_uploaded_yn,
                        a.pic_uploaded_dt,
                        a.pic_etc1,
                        a.pic_etc2
                          
                    from pic_dir_files a left outer join pic_gps b
                      on b.pic_gps_lat = a.pic_gps_lat
                      and b.pic_gps_lon = a.pic_gps_lon
                    order by 1,2,3,4
        """

        cursor.execute(sql)
        rslt = cursor.fetchall()

        if len(rslt) == 0:
            del myCur
            QMessageBox.information(self, 'No data', f"* [pic_dir_files] 테이블에 저장된 데이터가 없습니다.")

            return

        numcols = len(rslt[0])
        numrows = len(rslt)

        self.tblFiles.setColumnCount(numcols)
        self.tblFiles.setRowCount(numrows)

        # Loops to add values into QTableWidget
        for row in range(numrows):
            for column in range(numcols):
                # Check if value rslttime, if True convert to string
                if isinstance(rslt[row][column], datetime.datetime):
                    self.tblFiles.setItem(row, column,
                                          QTableWidgetItem((rslt[row][column].strftime('%d/%m/%Y %H:%M:%S'))))
                else:
                    self.tblFiles.setItem(row, column, QTableWidgetItem((str(rslt[row][column]))))

        del myCur

    #* 메시지 송수신 connect
    def f_metaCollectInit(self):
        photoMgr = self.photoMgr

        photoMgr.processMsgSender.connect(self.f_processMsgReceiver)
        photoMgr.processListSender.connect(self.f_processListReceiver)
        photoMgr.processFinSender.connect(self.f_processFinReceiver)

    # ------------------------------------------------------------------------------
    #* 1. 사진의 메타정보를 수집 -> pic_dir_files 테이블에 저장
    # ------------------------------------------------------------------------------
    def btnGetFileMetaInfo_Click(self):
        print('* btnGetFileMetaInfo_Click *******************')

        self.tblFiles.setRowCount(0)

        photoMgr = self.photoMgr


        search_folder = self.txtUrl.text()
        photoMgr.search_folder = search_folder
        strMediaType = self.cboMediaType.currentText()
        photoMgr.strMediaType = strMediaType

        #* run할때 쓰레드 함수를 구분해서 돌려야 한다.
        photoMgr.job_div = 'f_meta_collect_from_files'
        if self.chkDebug.isChecked():

            photoMgr.f_meta_collect_from_files()
        else:
            # 쓰레드 생성. 이러면 디버깅 안됨.
            photoMgr.start()

            self.btnGetFileMetaInfo.setEnabled(False)
            self.btnMakeGPSGroup.setEnabled(False)
            self.btnGetAddress.setEnabled(False)
            self.btnSavePictures.setEnabled(False)

            self.btnStop.setEnabled(True)


    def f_processFinReceiver(self, cnt):
        print('* photoManager Finished....')
        self.lblMsg.setText(f"* photoManager Finished.... [{cnt}]개 작업완료")
        #self.lblMsg.repaint()


        self.btnGetFileMetaInfo.setEnabled(True)
        self.btnMakeGPSGroup.setEnabled(True)
        self.btnGetAddress.setEnabled(True)
        self.btnSavePictures.setEnabled(True)

        self.btnStop.setEnabled(False)

        self.photoMgr.needStop = False

    def f_processListReceiver(self, file_info):



        #print("* f_processListReceiver() : ", file_info)
        rowPosition = self.tblFiles.rowCount()
        self.tblFiles.insertRow(rowPosition)

        item = QTableWidgetItem(file_info.pic_dir)

        self.tblFiles.setItem(rowPosition, 0, item)
        self.tblFiles.setItem(rowPosition, 1, QTableWidgetItem(file_info.pic_fname))
        self.tblFiles.setItem(rowPosition, 2, QTableWidgetItem(file_info.pic_day))

        self.tblFiles.setItem(rowPosition, 3, QTableWidgetItem(file_info.pic_time))
        self.tblFiles.setItem(rowPosition, 4, QTableWidgetItem(file_info.pic_day_of_week))
        self.tblFiles.setItem(rowPosition, 5, QTableWidgetItem(str(file_info.pic_width)))

        self.tblFiles.setItem(rowPosition, 6, QTableWidgetItem(str(file_info.pic_height)))

        if file_info.__class__.__name__ == CFILE_INFO:
            self.tblFiles.setItem(rowPosition, 7, QTableWidgetItem(file_info.pic_gps_yn))
            self.tblFiles.setItem(rowPosition, 8, QTableWidgetItem(str(file_info.pic_gps_lat)))
            self.tblFiles.setItem(rowPosition, 9, QTableWidgetItem(str(file_info.pic_gps_lon)))
            self.tblFiles.setItem(rowPosition, 10, QTableWidgetItem(file_info.pic_dir_adj))

            self.tblFiles.setItem(rowPosition, 12, QTableWidgetItem(file_info.pic_fname_adj))

            self.tblFiles.setItem(rowPosition, 13, QTableWidgetItem(str(file_info.pic_width_adj)))
            self.tblFiles.setItem(rowPosition, 14, QTableWidgetItem(str(file_info.pic_height_adj)))

            self.tblFiles.setItem(rowPosition, 15, QTableWidgetItem(file_info.pic_etc1))
            self.tblFiles.setItem(rowPosition, 16, QTableWidgetItem(file_info.pic_etc2))

        if file_info.__class__.__name__ == CMOVIE_FILE_INFO:
            self.tblFiles.setItem(rowPosition, 7, QTableWidgetItem(str(file_info.fps)))
            self.tblFiles.setItem(rowPosition, 8, QTableWidgetItem(str(file_info.movie_play_time)))
            self.tblFiles.setItem(rowPosition, 9, QTableWidgetItem(str(file_info.movie_file_size)))

            self.tblFiles.setItem(rowPosition, 10, QTableWidgetItem(file_info.pic_dir_adj))

            self.tblFiles.setItem(rowPosition, 11, QTableWidgetItem(file_info.pic_fname_adj))
            self.tblFiles.setItem(rowPosition, 12, QTableWidgetItem(str(file_info.pic_max_seq)))

            self.tblFiles.setItem(rowPosition, 13, QTableWidgetItem(file_info.pic_etc1))
            self.tblFiles.setItem(rowPosition, 14, QTableWidgetItem(file_info.pic_etc2))


        self.tblFiles.repaint()

        # ------------------------------------------------------------------------------
        # * 새로 추가되는 아이템이 화면에 보이게 처리....
        # ------------------------------------------------------------------------------
        self.tblFiles.scrollToItem(item)
        self.tblFiles.selectRow(rowPosition + 1)

    def f_processMsgReceiver(self, str):
        self.lblMsg.setText(f"{str}")
        self.lblMsg.repaint()
        #print(str)



    #-------------------------------------------------------------------------
    #* 여기 이하는 사용 안함....
    # -------------------------------------------------------------------------











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





    def btnDoWork_Click(self):
        pass

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
    dlg = MyPhotoUI2()
    dlg.exec_()
