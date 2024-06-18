# coding: utf-8
import json, AZMusicAPI
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import QTableWidgetItem, QCompleter
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import helper.config
import requests, os
from helper.config import cfg
from helper.getvalue import apipath, download_log, search_log, autoapi
from helper.inital import mkf
from helper.flyoutmsg import dlerr, dlwar

try:
    u = open(apipath, "r")
    data = json.loads(u.read())
    api = data["api"]
    q_api = data["q_api"]
    u.close()
except:
    api = autoapi
    q_api = ""
mkf()

def is_english_and_characters(input_string):
    return all(char.isalpha() or not char.isspace() for char in input_string)

class getlist(QThread):
    finished = pyqtSignal()

    @pyqtSlot()
    def run(self):
        u = open(search_log, "r")
        data = json.loads(u.read())
        u.close()
        text = data["text"]
        value = data["value"]
        api_value = data["api_value"]
        keywords = text
        
        if cfg.apicard.value == "NCMA":
            self.songInfos = AZMusicAPI.getmusic(keywords, number=value, api=api_value)
        else:
            self.songInfos = AZMusicAPI.getmusic(keywords, number=value, api=api_value, server="qqma")
        self.finished.emit()

def sethotlineEdit(lineEdit):
    if helper.config.cfg.hotcard.value:
        try:
            data = requests.get(api + "search/hot").json()["result"]["hots"]
            hot_song = []
            for i in data:
                hot_song.append(i["first"])
            completer = QCompleter(hot_song, lineEdit)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setMaxVisibleItems(10)
            lineEdit.setCompleter(completer)
        except:
            pass

def searchstart(lineEdit, parent, spinBox, lworker):
    # self.lworker.started.connect(
    #     lambda: self.lworker.run(text=self.lineEdit.text(), value=self.spinBox.value(), api_value=api))
    u = open(search_log, "w")
    if cfg.apicard.value == "NCMA":
        if api == "" or api is None:
            dlerr(outid=4, parent=parent)
            return "Error"
        u.write(json.dumps({"text": lineEdit.text(), "api_value": api, "value": spinBox.value()}))
    else:
        if q_api == "" or q_api is None:
            dlerr(outid=5, parent=parent)
            return "Error"
        u.write(json.dumps({"text": lineEdit.text(), "api_value": q_api, "value": spinBox.value()}))
    u.close()
    lworker.start()

def rundownload(primaryButton1, ProgressBar, tableView, parent, dworker, lworker):
        musicpath = cfg.get(cfg.downloadFolder)
        primaryButton1.setEnabled(False)
        ProgressBar.setHidden(False)
        ProgressBar.setValue(0)
        
        row = tableView.currentIndex().row()
        try:
            songdata = lworker.songInfos
            data = songdata[row]
        except:
            dlwar(content='您选中的行无数据', parent=parent)
            return 0
        
        song_id = data["id"]
        song = data["name"]
        singer = data["artists"]
        
        try:
            if os.path.exists(musicpath) == False:
                os.mkdir(musicpath)
        except:
            dlerr(outid=3, parent=parent)
            return 0
        
        # self.dworker.started.connect(lambda: self.dworker.run(id=song_id, api=api, song=song, singer=singer))
        u = open(download_log, 'w')
        if cfg.apicard.value == "NCMA":
            if api == "" or api is None:
                dlerr(outid=4, parent=parent)
                return "Error"
            u.write(json.dumps({"id": song_id, "api": api, "song": song, "singer": singer}))
        else:
            if q_api == "" or q_api is None:
                dlerr(outid=5, parent=parent)
                return "Error"
            u.write(json.dumps({"id": song_id, "api": q_api, "song": song, "singer": singer}))
        u.close()
        dworker.start()

def search(lworker, parent, tableView, spinBox):
        songInfos = lworker.songInfos
        if songInfos == "Error 0":
            dlwar(outid=0, parent=parent)
            return 0
        elif songInfos == "Error 1":
            dlwar(outid=1, parent=parent)
            return 0
        elif songInfos == "NetworkError":
            dlerr(outid=6, parent=parent)
            return 0
        
        tableView.setRowCount(spinBox.value())
        for i in range(len(songInfos)):
            data = songInfos[i]
            num = i + 1
            song_id = data["id"]
            title = data["name"]
            Artist = data["artists"]
            Album = data["album"]

            if len(title) > 8:
                title = title[:8] + "..."
            if len(Artist) > 8:
                Artist = Artist[:8] + "..."
            if len(Album) > 8:
                Album = Album[:8] + "..."
                
            data = []
            data.append(str(song_id))
            data.append(title)
            data.append(Artist)
            data.append(Album)
            for j in range(4):
                tableView.setItem(i, j, QTableWidgetItem(data[j]))
                
        tableView.resizeColumnsToContents()
        lworker.quit()