import codecs
import math
import os
import sys
import threading

from functools import partial
from core import utils

from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QPushButton, QSpinBox, QProgressBar, QListWidget, QLineEdit, QCheckBox

from core.youtube_stats import YouTubeStats

stop_thread = False


class ThreadProcess(QtCore.QThread):
    data_downloaded = QtCore.pyqtSignal(int)
    info_msg = QtCore.pyqtSignal(str)
    enable_btn = QtCore.pyqtSignal(bool)

    def __init__(self, url=None, num=None, music=False):
        QtCore.QThread.__init__(self)
        self.url = url
        self.num = num
        self.music = music

    def run(self):
        global stop_thread
        api_key = utils.get_api_key()
        list_url = self.url
        start = self.num
        idx = 0

        errors = []

        video_id = utils.url_to_id(list_url)  # id de la llista
        f = codecs.open(f"output/{video_id}.txt", "a", "utf8")
        token = "CAUQAQ"  # Token de la primera pag = CAUQAQ

        url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId={video_id}&key={api_key}&pageToken={token}"  # URL per treure dades JSON de la llista
        yt_stats = YouTubeStats(url)
        t_videos = yt_stats.get_total_videos()  # Total de videos a la llista
        v_page = yt_stats.get_page_videos()  # Nº de videos a la pàgina
        for i in range(math.ceil(t_videos / 50)):  # Per cada pàgina
            for y in range(v_page):  # Per cada video a la pàgina
                v_url = yt_stats.get_video_id(y)  # Pillar la ID del video
                v_url = utils.id_to_url(v_url)  # Pillar la URL del video
                title = yt_stats.get_video_title(y)  # Pillar el titol del video
                title = utils.title_to_underscore_title(title)  # Treure els espais i caracters
                self.info_msg.emit(f"{(y + (i * 50)) + 1} ({v_url}): {title}")
                if start == -2:
                    f.write(title + "\n")
                elif idx < start:  # No descarregar fins que arribi al video inicial
                    self.info_msg.emit(f"No descarregant... Next!")
                else:  # Un cop arribat al video inicial
                    self.info_msg.emit(f"Descarregant...")
                    try:
                        yt_stats.download_video(v_url, title)  # Descarregar el video
                        if self.music:
                            os.system(f"ffmpeg -i output/{title}.mp4 output/{title}.mp3")
                            os.remove(f"output/{title}.mp4")
                        self.info_msg.emit(f"FET! {(y + (i * 50)) + 1}/{t_videos}")
                        progress = int(((y + (i * 50)) + 1) / t_videos * 100)
                        self.data_downloaded.emit(progress)
                    except Exception as e:
                        errors.insert(-1, title)
                        self.info_msg.emit(f"Error descarregant {e}")
                    yt_stats = YouTubeStats(url)  # Tornar a obtenir les dades JSON perque no perdi la connexió entre video i video
                idx += 1
                if stop_thread:
                    break
            # print("Errors:", errors)
            try:
                token = yt_stats.get_next_token()  # Pillar el token de la propera pàgina
                url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId={video_id}&key={api_key}&pageToken={token}"  # Actualitzar la url JSON amb el nou token
                yt_stats = YouTubeStats(url)  # Dades JSON
                v_page = yt_stats.get_page_videos()  # Saber el Nº de videos a la nova pàgina
            except:
                if not errors:
                    self.info_msg.emit(f"Ha acabat sense errors! :)")
                else:
                    print("Ha acabat, hi ha hagut aquests errors:", errors)
                    self.info_msg.emit(f"Ha acabat, hi ha hagut aquests errors: {errors}")
            if stop_thread:
                break
        f.close()
        if stop_thread:
            self.enable_btn.emit(True)
            pass


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('ui/main.ui', self)  # Load the .ui file
        self.show()  # Show the GUI


class Main:
    def __init__(self):
        self.t = ThreadProcess()
        app = QtWidgets.QApplication(sys.argv)
        window = Ui()

        self.txt_url = window.findChild(QLineEdit, "txt_url")
        self.num_start = window.findChild(QSpinBox, "num_start")
        self.cb_music = window.findChild(QCheckBox, "cb_music")
        self.pbar = window.findChild(QProgressBar, "pbar")
        self.list_events = window.findChild(QListWidget, "list_events")
        self.btn_download = window.findChild(QPushButton, "btn_download")
        self.btn_download.clicked.connect(
            partial(self.check_fields, self.txt_url, self.num_start, self.pbar, self.list_events, self.btn_download))

        app.exec_()

    def _print_info(self, text):
        self.list_events.addItem(f"{text}")
        self.list_events.scrollToBottom()

    def _update_pbar(self, progress):
        self.pbar.setValue(progress)

    def _enable_btn(self, enable=True):
        if enable:
            self.btn_download.setText(f"Download")
        else:
            self.btn_download.setText(f"Stop")
        self.btn_download.setEnabled(True)

    def check_fields(self, txt_url, num_start, pbar, list_events, btn_download):
        global stop_thread
        if btn_download.text() == "Download":
            try:
                url = txt_url.text()
            except Exception as e:
                print(f"Error: {e}")
                return
            start = num_start.value()
            key = utils.get_api_key()
            if url and key:
                self._enable_btn(False)
                self.num_start.setEnabled(False)
                self.list_events.clear()
                stop_thread = False
                self.t = ThreadProcess(url, start, self.cb_music.isChecked())
                self.t.info_msg.connect(self._print_info)
                self.t.data_downloaded.connect(self._update_pbar)
                self.t.enable_btn.connect(self._enable_btn)
                self.t.start()
            else:
                print(f"Empty URL")
                return
        else:
            stop_thread = True
            self.btn_download.setText("Stopping...")
            self.btn_download.setEnabled(False)
            self.num_start.setEnabled(True)


if __name__ == '__main__':
    Main()
