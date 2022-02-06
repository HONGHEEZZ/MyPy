from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import os
import win32com.client
import time
from pytube import Playlist



my_dlg = uic.loadUiType("../ui/MyYoutube.ui")[0]


class CMyYoutube(QDialog, my_dlg):
    def __init__(self, parent=None):
        print("parent:", parent)
        super().__init__(parent)
        self.setupUi(self)
        # loadUi("test2",self)

        self.initUI()

        self.btnView.clicked.connect(self.btnView_Click)
        self.btnDownload.clicked.connect(self.btnDownload_Click)

        #블랙핑크
        self.txtPlayList.setText(r"https://www.youtube.com/playlist?list=OLAK5uy_lCA9bN3L-dnwrOcDKWMffau946jBXLozY")

        #경제용어
        self.txtPlayList.setText(r"https://www.youtube.com/playlist?list=PLtO7kiIkwW2RsezzwT9i2bQRYj-1uC52l")
        
        self.txtTargetDir.setText(r"D:\test\output")

        self.cboOutput.addItem("mp4")
        self.cboOutput.addItem("mp3")

    def initUI(self):
        self.setWindowTitle('MyYoutube')

        self.setMinimumSize(200, 200)

        self.tblFiles.setColumnCount(2)
        self.tblFiles.setHorizontalHeaderLabels(["Download List", "Video 제목"])

        self.tblFiles.setColumnWidth(0, 400)
        self.tblFiles.setColumnWidth(1, 300)

        self.progressBar.reset()


        # self.tblFiles.rowcount = 1

    def btnView_Click(self):

        self.lblStatus.setText("플레이 리스트 가져오는 중...")
        time.sleep(0.1)
        strPlayListUrl = self.txtPlayList.text()
        playlist = Playlist(strPlayListUrl)

        # 상태 진행바
        self.progressBar.setRange(0, len(playlist))


        self.tblFiles.setRowCount(len(playlist))
        
        #------------------------------------------------------------------------------
        #* url 가져오기
        # ------------------------------------------------------------------------------
        self.lblStatus.setText("Url 조회중...")
        row = 0
        for i, video in enumerate(playlist):
            self.tblFiles.setItem(i, 0, QTableWidgetItem(video))
            row = row + 1
            # 상태 진행바
            self.progressBar.setValue(row)

        self.lblStatus.setText("조회 완료...")

        # ------------------------------------------------------------------------------
        # * video 타이틀 가져오기
        # ------------------------------------------------------------------------------
        if not self.chkOnlyUrl.isChecked():
            self.lblStatus.setText("플레이 리스트 타이틀 조회중...")

            row = 0
            for i, video in enumerate(playlist.videos):
                self.tblFiles.setItem(i, 1, QTableWidgetItem(video.title))

                row = row + 1
                # 상태 진행바
                self.progressBar.setValue(row)
                self.lblStatus.setText(video.title + " 검색중....")


        
    def btnDownload_Click(self):


        strPlayListUrl = self.txtPlayList.text()
        playlist = Playlist(strPlayListUrl)

        pl_title = playlist.title

        target_dir = self.txtTargetDir.text()
        target_dir = target_dir + "/"

        # 상태 진행바
        self.progressBar.setRange(0, len(playlist))
        print("len(playlist):", len(playlist))

        row = 0

        # Loop through all videos in the playlist and download them
        for idx, video in enumerate(playlist.videos):
            print("title : %s" % video.title)
            self.tblFiles.setItem(row, 1, QTableWidgetItem(video.title))

            self.lblStatus.setText("{} 다운로드 중...".format(video.title))

            if self.cboOutput.currentText() == 'mp3':
                video.streams.filter(only_audio=True).first().download('{0}{1}'.format(target_dir, pl_title))
            elif self.cboOutput.currentText() == 'mp4':
                video.streams.filter().first().download('{0}{1}'.format(target_dir, pl_title))
            row = row + 1
            # 상태 진행바
            self.progressBar.setValue(row)

            time.sleep(0.1)

        self.lblStatus.setText("총 [{}]개 다운로드 완료...".format(row))

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