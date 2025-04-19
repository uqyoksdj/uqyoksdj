import os
import json
import sqlite3
import sys
import PyQt5
import cv2

from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QRegExp, QTime, QFileInfo
from PyQt5.QtGui import QPixmap, QPalette, QImage, QRegExpValidator, QDragEnterEvent, QDropEvent

from MainWindow import *
from DownloadWindow import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QToolTip, \
    QFileDialog, QSizePolicy, QProgressBar, QVBoxLayout, QAbstractItemView, QTableWidgetItem, \
    QStyledItemDelegate, QLineEdit, QItemDelegate, QTimeEdit
from PyQt5.QtGui import QMouseEvent
from download import ProcessVideo
from Database import DatabaseApp


class VideoClipThread(QThread):
    set_value = pyqtSignal(int)
    finished = pyqtSignal(int)

    def __init__(self, video_path, save_path, slider_start, slider_end, total_frames, fps):
        super().__init__()
        self.video_path = video_path
        self.save_path = save_path
        self.capture = cv2.VideoCapture(video_path)
        self.start_frame = slider_start
        self.end_frame = slider_end
        self.total_frames = total_frames
        self.fps = fps

    def run(self):
        width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 设置视频编解码器和输出参数
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        file_path = os.path.join(self.save_path, os.path.basename(self.video_path))
        output = cv2.VideoWriter(file_path, fourcc, self.fps, (width, height))

        # 定位到起始帧
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)

        # 逐帧写入输出视频
        for frame_index in range(self.start_frame, self.end_frame + 1):
            self.set_value.emit(frame_index)
            ret, frame = self.capture.read()
            if ret:
                output.write(frame)

        # 释放资源
        self.capture.release()
        output.release()
        self.finished.emit(1)
        print("视频剪辑完成。")


class MyLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.path = text
        text = os.path.basename(self.path)
        self.setObjectName(text)
        self.setStyleSheet('''QLabel { color: white; background-color: rgb(28, 28, 28);
                               border-radius: 10px; border: 0px solid white;}''')
        new_text = f"<span style=' color: white; font-size: 12pt;'>{text}</span><br/>"
        self.setText(new_text)
        self.setMinimumSize(210, 70)
        self.setMaximumSize(210, 70)
        self.slider_start = 0
        self.slider_end = 0
        self.setFocusPolicy(Qt.NoFocus)
        self.add_progress_bar()

    def add_progress_bar(self):
        layout = QVBoxLayout(self)
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        self.progress_bar.setMinimumSize(210, 70)
        self.progress_bar.setMaximumSize(210, 70)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

    def show_progress_bar(self, rgb):
        self.progress_bar.setVisible(True)
        # 使用百分号格式化来使用rgb值
        style_sheet = """
            QProgressBar {
                background-color: rgba(255, 255, 255, 0);
                border-radius: 10px;
                color: white;
                font-size: 15pt;
            }
            QProgressBar::chunk {
                background-color: rgba(%d, %d, %d, 128);
                border-radius: 10px;
            }
        """ % rgb  # 将rgb元组的每个元素分别作为参数传递

        self.progress_bar.setStyleSheet(style_sheet)


class TimeEditDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QTimeEdit(parent)
        editor.setDisplayFormat("HH:mm:ss")
        editor.setCalendarPopup(True)
        return editor

    def setEditorData(self, timeEdit, index):
        value = index.model().data(index, Qt.DisplayRole)
        time = QTime.fromString(value, "HH:mm:ss")
        timeEdit.setTime(time)

    def setModelData(self, timeEdit, model, index):
        time = timeEdit.time().toString("HH:mm:ss")
        model.setData(index, time, Qt.DisplayRole)


class FileNameValidatorDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        reg_ex = QRegExp("^[^\\\\/:*?\"<>|]*$")
        validator = QRegExpValidator(reg_ex, editor)
        editor.setValidator(validator)
        return editor


class DownloadWindow(QMainWindow):
    set_value = pyqtSignal(int)
    start_download = pyqtSignal(str)
    finished = pyqtSignal(int)
    errored = pyqtSignal(int)
    start_frame = pyqtSignal(float)
    end_frame = pyqtSignal(float)
    closed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setFixedSize(450, 600)
        self.ui = Ui_DownloadWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("下载")
        self.ui.pushButton_state.setEnabled(False)
        self.ui.pushButton_path.clicked.connect(self.Get_path)
        self.ui.pushButton_add.clicked.connect(self.Add)
        self.ui.tableWidget_2.setSelectionMode(QAbstractItemView.NoSelection)
        self.ui.tableWidget_1.horizontalHeader().setSectionsClickable(False)
        self.ui.tableWidget_2.horizontalHeader().setSectionsClickable(False)

        self.count1 = 0
        self.count2 = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.download)
        self.timer.start(200)

        self.downloading = False
        self.setAcceptDrops(True)  # 启用接受拖放事件

        delegate1 = FileNameValidatorDelegate(self.ui.tableWidget_1)
        delegate2 = TimeEditDelegate(self.ui.tableWidget_1)

        self.ui.tableWidget_1.setItemDelegateForColumn(0, delegate1)
        self.ui.tableWidget_1.setItemDelegateForColumn(1, delegate2)
        self.ui.tableWidget_1.setItemDelegateForColumn(2, delegate2)

        self.ui.lineEdit_1.setText('https://www.bilibili.com/video/BV1vG411Y7hW/')
        self.ui.lineEdit_2.setText(os.path.join(os.getcwd(), 'download'))

        self.con = sqlite3.connect("data/data.db")
        self.cur = self.con.cursor()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS record "
            "(id INTEGER PRIMARY KEY AUTOINCREMENT, file_name TEXT, url TEXT, start_time TEXT, end_time TEXT)")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if not QFileInfo(file_path).isDir():
                        event.acceptProposedAction()
                        return

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            file_urls = [url.toLocalFile() for url in event.mimeData().urls()]
            for file_url in file_urls:
                self.add_json(file_url)

    def add_json(self, path):
        if path.endswith('.json'):
            with open(path, 'r') as file:
                json_data = json.load(file)
            for block in json_data:
                file_name = block['file_name']
                url = block['url']
                start_time = block['start_time']
                end_time = block['end_time']
                self.ui.tableWidget_2.setItem(self.count1, 0, QTableWidgetItem(file_name))
                self.ui.tableWidget_2.setItem(self.count1, 1, QTableWidgetItem(url))
                self.ui.tableWidget_2.setItem(self.count1, 2, QTableWidgetItem(f'{start_time}-{end_time}'))
                self.ui.tableWidget_2.setItem(self.count1, 3, QTableWidgetItem('等待'))
                self.count1 += 1

    @staticmethod
    def get_new_filename(filename):
        base, ext = os.path.splitext(filename)
        new_filename = filename
        index = 1
        while os.path.exists(new_filename):
            new_filename = f"{base} ({index}){ext}"
            index += 1
        return new_filename

    def Get_path(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.Directory)
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.ui.lineEdit_2.setText(selected_files[0])

    def Add(self):
        rows = self.ui.tableWidget_1.rowCount()
        cols = self.ui.tableWidget_1.columnCount()
        table_data = []
        for row in range(rows):
            row_data = []
            for col in range(cols):
                item = self.ui.tableWidget_1.item(row, col)
                if item is not None:
                    if item.text() != '':
                        # print(item.text())
                        row_data.append(item.text())
                    else:
                        break
                else:
                    break
            table_data.append(row_data)
        table_data = [sublist for sublist in table_data if sublist]
        # print(len(table_data))
        self.ui.tableWidget_1.clearContents()

        for sublist in table_data:
            start_hours, start_minutes, start_seconds = sublist[1].split(':')
            end_hours, end_minutes, end_seconds = sublist[2].split(':')
            start_time = int(start_hours) * 3600 + int(start_minutes) * 60 + int(start_seconds)
            end_time = int(end_hours) * 3600 + int(end_minutes) * 60 + int(end_seconds)
            self.ui.tableWidget_2.setItem(self.count1, 0, QTableWidgetItem(sublist[0]))
            self.ui.tableWidget_2.setItem(self.count1, 1, QTableWidgetItem(self.ui.lineEdit_1.text()))
            self.ui.tableWidget_2.setItem(self.count1, 2, QTableWidgetItem(f'{start_time}-{end_time}'))
            self.ui.tableWidget_2.setItem(self.count1, 3, QTableWidgetItem('等待'))
            self.count1 += 1

    def download(self):
        if not self.downloading:
            if self.count2 < self.count1 != 0:
                self.downloading = True
                self.file_name = self.ui.tableWidget_2.item(self.count2, 0).text()
                self.url = self.ui.tableWidget_2.item(self.count2, 1).text()
                self.start_time = int(self.ui.tableWidget_2.item(self.count2, 2).text().split('-')[0])
                self.end_time = int(self.ui.tableWidget_2.item(self.count2, 2).text().split('-')[1])
                if self.ui.lineEdit_2.text() != '':
                    path = os.path.join(
                        self.ui.lineEdit_2.text(), self.ui.tableWidget_2.item(self.count2, 0).text() + '.mp4')
                    path = self.get_new_filename(path)
                    self.p = ProcessVideo(self.url, self.start_time, self.end_time, path)
                    self.p.daemon = True
                    self.p.start()
                    self.start_download.emit(path)
                    self.p.set_value.connect(self.update_table)
                    self.p.finished.connect(self.download_finished)
                    self.p.start_frame.connect(lambda start_frame: self.start_frame.emit(start_frame))
                    self.p.end_frame.connect(lambda end_frame: self.end_frame.emit(end_frame))
                    self.p.error.connect(self.error)

    def update_table(self, progress):
        self.ui.tableWidget_2.setItem(self.count2, 3, QTableWidgetItem(f'{progress}%'))
        self.set_value.emit(progress)

    def download_finished(self, finished):
        self.downloading = False
        self.ui.tableWidget_2.setItem(self.count2, 3, QTableWidgetItem('完成'))
        self.count2 += 1
        self.finished.emit(finished)
        self.cur.execute("SELECT * FROM record WHERE file_name = ? AND url = ? AND start_time = ? AND end_time = ?",
                         (self.file_name, self.url, self.start_time, self.end_time))
        result = self.cur.fetchone()

        if result is None:
            self.cur.execute("INSERT INTO record (file_name, url, start_time, end_time) VALUES (?, ?, ?, ?)",
                             (self.file_name, self.url, self.start_time, self.end_time))
            self.con.commit()
        else:
            print('数据已存在')

    def error(self, error):
        self.downloading = False
        self.ui.tableWidget_2.setItem(self.count2, 3, QTableWidgetItem('错误'))
        self.count2 += 1
        self.errored.emit(error)

    def closeEvent(self, event):
        self.closed.emit(1)
        self.cur.close()
        self.con.close()
        event.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("主界面")
        self.save_path = os.path.join(os.getcwd(), 'cut')

        self.ui.frame_slider.mousePressEvent = self.SliderFrameClicked  # 外部重写鼠标点击事件
        self.ui.pushButton_start_clip.setToolTip('在当前时间开始该片段')
        self.ui.pushButton_start_clip.clicked.connect(self.Start_clip_clicked)
        self.ui.pushButton_end_clip.setToolTip('在当前时间结束该片段')
        self.ui.pushButton_end_clip.clicked.connect(self.End_clip_clicked)
        self.ui.pushButton_next_frame.setToolTip('前进一帧')
        self.ui.pushButton_next_frame.clicked.connect(self.Next_frame)
        self.ui.pushButton_last_frame.setToolTip('后退一帧')
        self.ui.pushButton_last_frame.clicked.connect(self.Last_frame)
        self.ui.pushButton_slip_start.setToolTip('跳转到当前片段开始时间')
        self.ui.pushButton_slip_start.clicked.connect(self.Slip_start)
        self.ui.pushButton_slip_end.setToolTip('跳转到当前片段结束时间')
        self.ui.pushButton_slip_end.clicked.connect(self.Slip_end)
        self.ui.pushButton_open_file.setToolTip('打开文件')
        self.ui.pushButton_open_file.clicked.connect(self.select_file)
        self.ui.pushButton_play_and_stop.clicked.connect(self.play_and_stop)
        self.ui.pushButton_save_path.setToolTip('更改保存路径')
        self.ui.pushButton_save_path.clicked.connect(self.Set_save_path)
        self.ui.pushButton_save_path.setText(self.save_path)
        self.ui.pushButton_export.clicked.connect(self.Export)
        self.ui.pushButton_download.clicked.connect(self.Download)
        self.ui.pushButton_sql.clicked.connect(self.Sql)

        self.Set_page_1()
        self.ui.pushButton_working.clicked.connect(self.Set_page_1)
        self.ui.pushButton_finished.clicked.connect(self.Set_page_2)
        self.layout_1 = QVBoxLayout(self.ui.scrollAreaWidget_1)
        self.layout_1.setAlignment(QtCore.Qt.AlignTop)
        self.layout_2 = QVBoxLayout(self.ui.scrollAreaWidget_2)
        self.layout_2.setAlignment(QtCore.Qt.AlignTop)

        self.can_cut = False
        self.label_clicked = MyLabel('')
        self.label_delete = MyLabel('')
        self.is_cuting = False
        self.is_open_download = False
        self.is_open_database = False

        self.ui.label_VideoPlayer.setAlignment(Qt.AlignCenter)
        sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.ui.label_VideoPlayer.setSizePolicy(sizePolicy)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame_video)
        self.timer_always = QTimer(self)
        self.timer_always.start(50)
        self.timer_always.timeout.connect(self.update_frame_other)

        palette = QPalette()
        palette.setColor(QPalette.ToolTipBase, Qt.black)  # 背景颜色设置为黑色
        palette.setColor(QPalette.ToolTipText, Qt.white)  # 文字颜色设置为白色
        palette.setColor(QPalette.Light, Qt.white)  # 边框颜色设置为白色
        QToolTip.setPalette(palette)

        self.is_playing = False
        self.is_open_media = False
        self.capture = None
        self.total_frames = 60
        self.slider_start = 0
        self.slider_end = 0
        self.slider_x = 0  # 理解为读取了几帧，从0到总帧数，当为总帧数减一时显示最后一帧，为总帧数时视频播放完毕
        self.video_path = ''
        self.ui.label_line.setGeometry(0, 0, 1, 50)
        self.played = False

        self.disableFocusAndKeys(self)  # 禁用焦点框和按键功能

        self.frame = None
        self.show()

    def keyPressEvent(self, event):
        key = event.key()
        if event.key() == Qt.Key_Space:
            self.play_and_stop()
        elif key == Qt.Key_I:
            self.Start_clip_clicked()
        elif key == Qt.Key_O:
            self.End_clip_clicked()
        elif key == Qt.Key_Left:
            self.Last_frame()
        elif key == Qt.Key_Right:
            self.Next_frame()
        elif key == Qt.Key_Home:
            self.Slip_start()
        elif key == Qt.Key_End:
            self.Slip_end()

    def disableFocusAndKeys(self, widget):
        # 禁用焦点框和按键功能
        widget.setFocusPolicy(Qt.NoFocus)
        # 递归遍历子控件
        for child in widget.findChildren(QWidget):
            self.disableFocusAndKeys(child)

    def play_and_stop(self):
        if self.played:
            self.played = False
            self.slider_x_change(0)
        if not self.is_playing and self.is_open_media:
            self.ui.pushButton_play_and_stop.setIcon(QtGui.QIcon(QtGui.QPixmap(":/icons/icons/暂停.png")))
            self.is_playing = True
            self.timer.start(int(1000 / self.fps))  # 设置定时器时间间隔
        elif self.is_playing:
            self.stop()

    def stop(self):
        self.ui.pushButton_play_and_stop.setIcon(QtGui.QIcon(QtGui.QPixmap(":/icons/icons/播放.png")))
        self.is_playing = False
        self.timer.stop()

    def select_file(self):
        self.video_path, _ = QFileDialog.getOpenFileName(self, '选择文件', os.path.expanduser('.mp4'))
        if self.video_path.endswith('.mp4'):
            self.load_media('open')

    def load_media(self, source):
        if self.video_path != '':
            if self.capture is not None:
                self.capture.release()
            self.capture = cv2.VideoCapture(self.video_path)
            self.fps = self.capture.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
            self.is_open_media = True
            self.slider_start = 0
            self.slider_end = self.total_frames - 1
            self.slider_x_change(0)
            self.stop()

            if source == 'open':
                self.can_cut = False
                self.label_clicked.setStyleSheet('''QLabel { color: white; background-color: rgb(28, 28, 28);
                                                    border-radius: 10px; border: 0px solid white;}''')
                self.label_clicked = MyLabel('')
            elif source == 'working_click':
                self.can_cut = True
                self.slider_start = self.label_clicked.slider_start
                self.slider_x_change(self.slider_start)
                self.slider_end = self.label_clicked.slider_end
                self.label_clicked.setText(self.get_text())
            elif source == 'finished_click':
                self.can_cut = False

    def Next_frame(self):
        if self.is_open_media:
            self.slider_x_change(min(self.slider_x + 1, self.total_frames))

    def Last_frame(self):
        if self.is_open_media:
            self.slider_x_change(max(0, self.slider_x - 1))

    def Slip_start(self):
        if self.is_open_media:
            self.slider_x_change(self.slider_start)

    def Slip_end(self):
        if self.is_open_media:
            self.slider_x_change(self.slider_end)

    def SliderFrameClicked(self, event: QMouseEvent):
        self.slider_x_change(
            min(int((event.x() / self.ui.frame_slider.size().width() * self.total_frames)), self.total_frames - 1))

    def Start_clip_clicked(self):
        if self.is_open_media and self.can_cut:
            if self.slider_x >= self.slider_end:
                self.slider_end = self.total_frames - 1
                self.label_clicked.slider_end = self.total_frames - 1
            self.slider_start = self.slider_x
            self.label_clicked.slider_start = self.slider_x
            self.label_clicked.setText(self.get_text())

    def End_clip_clicked(self):
        if self.is_open_media and self.can_cut:
            if self.slider_x <= self.slider_start:
                self.slider_start = 0
                self.label_clicked.slider_start = 0
            self.slider_end = self.slider_x
            self.label_clicked.slider_end = self.slider_x
            self.label_clicked.setText(self.get_text())

    def Set_save_path(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.Directory)
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.save_path = selected_files[0]
                self.ui.pushButton_save_path.setText(self.save_path)

    def Export(self):
        if not self.is_cuting and self.can_cut:
            self.video_clip_thread = VideoClipThread(
                self.video_path, self.save_path, self.slider_start, self.slider_end, self.total_frames, self.fps)
            self.video_clip_thread.daemon = True
            self.video_clip_thread.finished.connect(self.Cut_finished)
            self.is_cuting = True
            self.video_clip_thread.start()

            self.label_clicked.setStyleSheet('''QLabel { color: white; background-color: rgb(28, 28, 28);
                                                   border-radius: 10px; border: 0px solid white;}''')
            self.label_clicked.setDisabled(True)
            self.label_delete = self.label_clicked
            self.label_delete.show_progress_bar((150, 103, 81))
            self.label_delete.progress_bar.setRange(self.slider_start, self.slider_end)
            self.video_clip_thread.set_value.connect(lambda value: self.label_delete.progress_bar.setValue(value))

            label_list = self.ui.scrollAreaWidget_1.findChildren(QLabel)
            if len(label_list) == 1:
                self.label_clicked = MyLabel('')
                self.is_playing = False
                self.is_open_media = False
                self.frame = None
                self.slider_x_change(0)
                self.slider_start = 0
                self.slider_end = 0
            else:
                for label in label_list:
                    if label != self.label_delete:
                        self.labelClicked(label, 'working')  # 模拟鼠标点击
                        break
            self.stop()
        elif self.is_cuting and self.can_cut:
            print('有任务进行中')
        elif not self.can_cut:
            print('当前不可剪辑')

    def Cut_finished(self, finished):
        self.is_cuting = False
        label = self.create_finished_label(self.label_delete.path, self.ui.scrollAreaWidget_2)
        self.layout_2.addWidget(label)
        self.label_delete.deleteLater()

    def Download(self):
        if not self.is_open_download:
            self.is_open_download = True
            self.Download_window = DownloadWindow()
            self.Download_window.show()
            self.Download_window.start_download.connect(self.load_add)
            self.Download_window.finished.connect(self.load_finished)
            self.Download_window.errored.connect(self.load_error)
            self.Download_window.closed.connect(lambda: setattr(self, 'is_open_download', False))

    def Sql(self):
        if not self.is_open_database:
            self.is_open_database = True
            self.Database_window = DatabaseApp()
            self.Database_window.show()
            self.Database_window.closed.connect(lambda: setattr(self, 'is_open_database', False))

    def load_error(self, errored):
        self.label_load.deleteLater()

    def load_finished(self, finished):
        self.label_load.progress_bar.setVisible(False)
        self.label_load.setDisabled(False)
        capture = cv2.VideoCapture(self.label_load.path)
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        capture.release()
        self.label_load.slider_start = int(self.label_load.start_frame * total_frames)
        self.label_load.slider_end = int(self.label_load.end_frame * total_frames)

    def load_working(self):
        self.label_load.show_progress_bar((0, 255, 0))
        self.Download_window.set_value.connect(lambda value: self.label_load.progress_bar.setValue(value))

    def load_add(self, video_path):
        label = self.create_working_label(video_path, self.ui.scrollAreaWidget_1)
        label.setDisabled(True)
        self.Download_window.start_frame.connect(self.set_label_start)
        self.Download_window.end_frame.connect(self.set_label_end)
        self.label_load = label
        self.load_working()
        self.layout_1.addWidget(label)

    def set_label_start(self, start_frame):
        self.label_load.start_frame = start_frame

    def set_label_end(self, end_frame):
        self.label_load.end_frame = end_frame

    def get_text(self):
        text = [os.path.basename(self.video_path)]
        time_start = self.get_time(self.label_clicked.slider_start)
        time_end = self.get_time(self.label_clicked.slider_end)
        text.append(f'{time_start[0]:02d}:{time_start[1]:02d}:{time_start[2]:02d}.{time_start[3]:03d}-' +
                    f'{time_end[0]:02d}:{time_end[1]:02d}:{time_end[2]:02d}.{time_end[3]:03d}')
        text.append(self.label_clicked.slider_end - self.label_clicked.slider_start)
        text = f"""
                    <span style=' color: white; font-size: 12pt;'>{text[0]}</span><br/>
                    <span style=' color: rgb(160, 160, 160); font-size: 9pt;'>{text[1]}</span><br/>
                    <span style=' color: rgb(160, 160, 160); font-size: 10pt;'>{int(text[2])}帧</span>
                    """
        return text

    def get_time(self, slider):
        seconds = int(slider / self.fps)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        ms = int((slider / self.fps) * 1000) % 1000
        return [hours, minutes, seconds, ms]

    def update_frame_video(self):
        if self.is_playing:
            self.show_frame()
            # 更新进度条
            current_position = int(self.capture.get(cv2.CAP_PROP_POS_FRAMES))
            self.slider_x_change(current_position, True)

    def slider_x_change(self, new_slider_x: int, playing_change=False):
        self.slider_x = new_slider_x

        if self.is_open_media:
            if self.slider_x < self.total_frames and self.played:
                self.played = False
            if not playing_change:
                self.capture.set(cv2.CAP_PROP_POS_FRAMES, self.slider_x)
            if self.slider_x < self.total_frames:
                ret, self.frame = self.capture.read()
            elif self.slider_x >= self.total_frames:
                self.ui.pushButton_play_and_stop.setIcon(QtGui.QIcon(QtGui.QPixmap(":/icons/icons/播放.png")))
                self.is_playing = False
                self.timer.stop()
                self.played = True

            time = self.get_time(self.slider_x)
            self.ui.label_time.setText(
                f"{time[0]:02d}:{time[1]:02d}:{time[2]:02d}.{time[3]:03d}")

    def update_frame_other(self):
        self.ui.label_select.setGeometry(
            int(self.slider_start / self.total_frames * self.ui.frame_slider.size().width()), 0,
            int(self.slider_end / self.total_frames * self.ui.frame_slider.size().width()) -
            int(self.slider_start / self.total_frames * self.ui.frame_slider.size().width()), 50)
        self.ui.label_line.setGeometry(
            int(self.slider_x / self.total_frames * self.ui.frame_slider.size().width()), 0, 1, 50)
        self.ui.label_time.setGeometry(self.ui.frame_slider.size().width() // 2 - 62, 10, 124, 30)

        if not self.is_playing:
            self.show_frame()

    def show_frame(self):
        if self.frame is not None:
            frame = self.resize_frame(self.frame, self.ui.label_VideoPlayer.width(), self.ui.label_VideoPlayer.height())
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 显示视频帧
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.ui.label_VideoPlayer.setPixmap(pixmap)
        else:
            self.ui.label_VideoPlayer.clear()

    @staticmethod
    def resize_frame(frame, width, height):
        frame_width, frame_height = frame.shape[1], frame.shape[0]
        label_ratio = width / height
        frame_ratio = frame_width / frame_height

        if frame_ratio > label_ratio:
            # 宽铺满，高自适应
            new_height = int(width / frame_ratio)
            frame = cv2.resize(frame, (width, new_height))
        else:
            # 高铺满，宽自适应
            new_width = int(height * frame_ratio)
            frame = cv2.resize(frame, (new_width, height))

        return frame

    def Set_page_1(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.frame_working.setStyleSheet('background: rgb(104, 84, 75);')
        self.ui.frame_finished.setStyleSheet('')

    def Set_page_2(self):
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.frame_finished.setStyleSheet('background: rgb(104, 84, 75);')
        self.ui.frame_working.setStyleSheet('')

    def create_working_label(self, text, parent):
        label = MyLabel(text, parent)
        label.mousePressEvent = lambda _: self.labelClicked(label, 'working')
        return label

    def create_finished_label(self, text, parent):
        label = MyLabel(text, parent)
        label.mousePressEvent = lambda _: self.labelClicked(label, 'finished')
        return label

    def labelClicked(self, label, source):
        self.label_clicked.setStyleSheet('''QLabel { color: white; background-color: rgb(28, 28, 28);
                               border-radius: 10px; border: 0px solid white;}''')
        self.label_clicked = label
        self.label_clicked.setStyleSheet('''QLabel { color: white; background-color: rgb(28, 28, 28);
                               border-radius: 10px; border: 1px solid white;}''')
        if source == 'working':
            self.video_path = self.label_clicked.path
            self.load_media('working_click')
        elif source == 'finished':
            self.video_path = os.path.join(self.save_path, os.path.basename(self.label_clicked.path))
            self.load_media('finished_click')

    def closeEvent(self, event):
        if self.is_open_download:
            self.Download_window.close()
        if self.is_open_database:
            self.Database_window.close()
        event.accept()


def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)


if __name__ == '__main__':
    try:
        dirname = os.path.dirname(PyQt5.__file__)
        qt_dir = os.path.join(dirname, 'Qt5', 'plugins', 'platforms')
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_dir

        create_folder_if_not_exists(os.path.join(os.getcwd(), 'cut'))
        create_folder_if_not_exists(os.path.join(os.getcwd(), 'download'))
        create_folder_if_not_exists(os.path.join(os.getcwd(), 'data'))

        app = QApplication(sys.argv)
        win = MainWindow()
        # win.show()
        sys.exit(app.exec_())
    except Exception as e:
        print('出错了:', str(e))
