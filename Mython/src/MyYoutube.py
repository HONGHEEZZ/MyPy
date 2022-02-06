from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import os
import win32com.client
import time
from pytube import YouTube
from pytube import Playlist
from pytube.exceptions import VideoPrivate

my_dlg = uic.loadUiType("./ui/MyYoutube.ui")[0]


class CMyYoutube(QDialog, my_dlg):
    def __init__(self, parent=None):
        print("parent:", parent)
        super().__init__(parent)
        self.setupUi(self)
        # loadUi("test2",self)

        self.initUI()

        self.btnView.clicked.connect(self.btnView_Click)
        self.btnDownload.clicked.connect(self.btnDownload_Click)

        self.btnDownOnlyOne.clicked.connect(self.btnDownOnlyOne_Click)



        # 체크박스
        self.chkAll.clicked.connect(self.chkAll_Click)

        # 블랙핑크
        self.txtPlayList.setText(r"https://www.youtube.com/playlist?list=OLAK5uy_lCA9bN3L-dnwrOcDKWMffau946jBXLozY")

        # 경제용어
        self.txtPlayList.setText(r"https://www.youtube.com/playlist?list=PLtO7kiIkwW2RsezzwT9i2bQRYj-1uC52l")

        # 영어회화 100일의 기적
        self.txtPlayList.setText(r"https://youtube.com/playlist?list=PLAkBgrW5qY0S0e0aEDhtvG82j3_0FPhW8")

        #영어회화 100일의 기적 리스트
        #https://www.youtube.com/watch?v=eSFKOOW6I7Q&list=PLAkBgrW5qY0ROKRZQO-vpJQ6kYdYT5Hss

        #머신러닝
        #self.txtPlayList.setText(r"https://www.youtube.com/watch?v=vcCaSBJpsHk&list=PLS8gIc2q83OjStGjdTF2LZtc0vefCAbnX")

        #전기 기능사 이론
        #self.txtPlayList.setText(r"https://www.youtube.com/watch?v=cDKfNHv0LTo&list=PLt-9xySRVAc3gEs_55kY1UVTKlRMrFqSg")


        self.txtTargetDir.setText(r"D:\test\output")

        self.cboOutput.addItem("mp4")
        self.cboOutput.addItem("mp3")

    def initUI(self):
        self.setWindowTitle('MyYoutube')

        self.setMinimumSize(200, 200)

        self.tblFiles.setColumnCount(3)
        self.tblFiles.setHorizontalHeaderLabels([" ", "Download List", "Video 제목"])

        # 1칼럼의 체크박스
        self.m_checkBox = []

        self.chkAll.setChecked(True)
        self.tblFiles.setColumnWidth(0, 30)
        self.tblFiles.setColumnWidth(1, 400)
        self.tblFiles.setColumnWidth(2, 300)

        self.progressBar.reset()

        # self.tblFiles.rowcount = 1

    # ------------------------------------------------------------------------------
    # * 전체 선택 / 해제
    # ------------------------------------------------------------------------------
    def chkAll_Click(self):
        print("******checked.....")
        if len(self.m_checkBox) == 0: return

        value = self.chkAll.isChecked()
        for chk in self.m_checkBox:
            chk.setChecked(value)

    def inertCheckBoxToTable(self):

        self.m_checkBox = []
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

    def btnView_Click(self):

        self.lblStatus.setText("플레이 리스트 가져오는 중...")
        time.sleep(0.1)
        strPlayListUrl = self.txtPlayList.text()
        playlist = Playlist(strPlayListUrl)

        # 상태 진행바
        self.progressBar.setRange(0, len(playlist))

        self.tblFiles.setRowCount(len(playlist))

        # ------------------------------------------------------------------------------
        # * url 가져오기
        # ------------------------------------------------------------------------------
        self.lblStatus.setText("Url 조회중...")
        row = 0
        for i, video in enumerate(playlist):
            self.tblFiles.setItem(i, 1, QTableWidgetItem(video))
            row = row + 1
            # 상태 진행바
            self.progressBar.setValue(row)

            self.tblFiles.repaint()

        # 1칼럼에 체크박스 추가
        self.inertCheckBoxToTable()

        self.lblStatus.setText("조회 완료...")

        # ------------------------------------------------------------------------------
        # * video 타이틀 가져오기
        # ------------------------------------------------------------------------------
        if not self.chkOnlyUrl.isChecked():
            self.lblStatus.setText("플레이 리스트 타이틀 조회중...")

            videos = iter(playlist.videos)



            row = 0

            while True:

                strVideoTitle = ''

                # 아이템 상태 확인
                try:
                    video = next(videos)
                    chk = video.check_availability()
                except StopIteration as e:
                    break
                except Exception as e:  # 모든 예외의 에러 메시지를 출력할 때는 Exception을 사용
                    print('예외가 발생했습니다.', e)
                    strVideoTitle = repr(e)
                    strVideoTitle = '***[ERROR]' + strVideoTitle


                else:
                    strVideoTitle = video.title
                finally:

                    item = QTableWidgetItem()
                    item.setData(Qt.EditRole, strVideoTitle)
                    print(f"[{row}]", strVideoTitle)
                    self.tblFiles.setItem(row, 2, item)

                    # ------------------------------------------------------------------------------
                    # * 새로 추가되는 아이템이 화면에 보이게 처리....
                    # ------------------------------------------------------------------------------
                    self.tblFiles.scrollToItem(item)
                    self.tblFiles.selectRow(row)

                    row = row + 1
                    # 상태 진행바
                    self.progressBar.setValue(row)
                    self.lblStatus.setText(strVideoTitle + "....")
                    self.tblFiles.repaint()

        QMessageBox.information(self, '조회완료', "총 [{}]개 리스트 조회 완료...".format(row), QMessageBox.Yes)



    def btnDownOnlyOne_Click(self):
        url = self.txtPlayList.text()
        target_dir = self.txtTargetDir.text()
        target_dir = target_dir + "/"


        yt = YouTube(url)


        stream = yt.streams.filter(progressive=True, file_extension='mp4') # 프로그레시브 방식의 인코딩, 파일 포맷은 MP4
        #stream = yt.streams.filter()
        stream = stream.order_by('resolution')  # 영상 해상도 순으로 정렬
        stream = stream.desc()  #내림 차순으로 정렬
        stream = stream.first() #가장 첫번째 스트림 (가장 고화질)
        #stream = stream.download(output_path=target_dir)

        print("영상 제목 : ", yt.title)
        print("영상 길이 : ", yt.length)
        print("영상 평점 : ", yt.rating)
        print("영상 썸네일 링크 : ", yt.thumbnail_url)
        print("영상 조회수 : ", yt.views)
        print("영상 설명 : ", yt.description)

        self.lblStatus.setText("{} 다운로드 중...".format(yt.title))
        stream.download(output_path=target_dir)  # 영상 다운로드
        self.lblStatus.setText("{} 다운로드 완료...".format(yt.title))


    def btnDownload_Click(self):

        strPlayListUrl = self.txtPlayList.text()
        playlist = Playlist(strPlayListUrl)

        pl_title = playlist.title

        target_dir = self.txtTargetDir.text()
        target_dir = target_dir + "/"

        # 상태 진행바
        self.progressBar.setRange(0, len(playlist))
        print("len(playlist):", len(playlist))

        # Loop through all videos in the playlist and download them

        videos = iter(playlist.videos)
        row = 0
        err_msg = ''
        while True:

            # 아이템 상태 확인
            try:

                video = next(videos)
                chk = video.check_availability()

                # 체크박스가 선택되어 있지 않으면 건너뛴다...
                if self.m_checkBox[row].isChecked() == False: continue


            except StopIteration as e:
                break
            except Exception as e:  # 모든 예외의 에러 메시지를 출력할 때는 Exception을 사용
                print('예외가 발생했습니다.', e)
                err_msg = repr(e)
                err_msg = '***[ERROR]' + err_msg

                self.lblStatus.setText(f"{err_msg} ")
            else:
                print("title : %s" % video.title)
                self.tblFiles.setItem(row, 2, QTableWidgetItem(video.title))

                self.lblStatus.setText("{} 다운로드 중...".format(video.title))

                if self.cboOutput.currentText() == 'mp3':
                    video.streams.filter(only_audio=True).first().download('{0}{1}'.format(target_dir, pl_title))
                elif self.cboOutput.currentText() == 'mp4':

                    #video.streams.filter().first().download('{0}{1}'.format(target_dir, pl_title))

                    stream = video.streams.filter(progressive=True, file_extension='mp4')  # 프로그레시브 방식의 인코딩, 파일 포맷은 MP4
                    stream = stream.order_by('resolution')  # 영상 해상도 순으로 정렬
                    stream = stream.desc()  # 내림 차순으로 정렬
                    stream = stream.first()  # 가장 첫번째 스트림 (가장 고화질)
                    stream.download('{0}{1}'.format(target_dir, pl_title))

            finally:

                row = row + 1
                # 상태 진행바
                self.progressBar.setValue(row)

                time.sleep(0.1)

        self.lblStatus.setText("총 [{}]개 다운로드 완료...".format(row))
        reply = QMessageBox.question(self, '다운로드 완료', "총 [{}]개 다운로드 완료...".format(row), QMessageBox.Yes)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ex = CMyYoutube()
    ex.show()
    sys.exit(app.exec_())

'''


* 파이썬 ui 참고 자료 - wikidoc
- PyQt5 Tutorial - 파이썬으로 만드는 나만의 GUI 프로그램
- 초보자를 위한 Python GUI 프로그래밍 - PyQt5
- python_ Cheat Sheet

'''