# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DownloadWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DownloadWindow(object):
    def setupUi(self, DownloadWindow):
        DownloadWindow.setObjectName("DownloadWindow")
        DownloadWindow.resize(450, 600)
        self.centralwidget = QtWidgets.QWidget(DownloadWindow)
        self.centralwidget.setStyleSheet("background-color:rgb(255,255,255);")
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setMinimumSize(QtCore.QSize(0, 100))
        self.frame.setMaximumSize(QtCore.QSize(16777215, 100))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setLineWidth(0)
        self.frame.setObjectName("frame")
        self.lineEdit_1 = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_1.setGeometry(QtCore.QRect(10, 10, 400, 30))
        self.lineEdit_1.setStyleSheet("    QLineEdit {\n"
"        border: 2px solid rgb(40, 176, 221);\n"
"        border-radius: 10px;\n"
"        padding: 2px 8px;\n"
"    }")
        self.lineEdit_1.setCursorPosition(0)
        self.lineEdit_1.setObjectName("lineEdit_1")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_2.setGeometry(QtCore.QRect(10, 50, 400, 30))
        self.lineEdit_2.setStyleSheet("    QLineEdit {\n"
"        border: 2px solid rgb(40, 176, 221);\n"
"        border-radius: 10px;\n"
"        padding: 2px 8px;\n"
"    }")
        self.lineEdit_2.setMaxLength(32767)
        self.lineEdit_2.setPlaceholderText("请输入文件保存位置......")
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.pushButton_state = QtWidgets.QPushButton(self.frame)
        self.pushButton_state.setGeometry(QtCore.QRect(415, 10, 30, 30))
        self.pushButton_state.setStyleSheet("border: none;")
        self.pushButton_state.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/正确.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/正确.png"), QtGui.QIcon.Disabled, QtGui.QIcon.Off)
        self.pushButton_state.setIcon(icon)
        self.pushButton_state.setIconSize(QtCore.QSize(30, 30))
        self.pushButton_state.setObjectName("pushButton_state")
        self.pushButton_path = QtWidgets.QPushButton(self.frame)
        self.pushButton_path.setGeometry(QtCore.QRect(415, 50, 30, 30))
        self.pushButton_path.setStyleSheet("border: none;")
        self.pushButton_path.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/保存.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_path.setIcon(icon1)
        self.pushButton_path.setObjectName("pushButton_path")
        self.verticalLayout.addWidget(self.frame)
        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setMinimumSize(QtCore.QSize(0, 200))
        self.frame_2.setMaximumSize(QtCore.QSize(16777215, 200))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setLineWidth(0)
        self.frame_2.setObjectName("frame_2")
        self.tableWidget_1 = QtWidgets.QTableWidget(self.frame_2)
        self.tableWidget_1.setGeometry(QtCore.QRect(0, 0, 450, 150))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget_1.sizePolicy().hasHeightForWidth())
        self.tableWidget_1.setSizePolicy(sizePolicy)
        self.tableWidget_1.setMinimumSize(QtCore.QSize(0, 150))
        self.tableWidget_1.setMaximumSize(QtCore.QSize(16777215, 150))
        self.tableWidget_1.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.tableWidget_1.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tableWidget_1.setEditTriggers(QtWidgets.QAbstractItemView.AnyKeyPressed|QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.EditKeyPressed)
        self.tableWidget_1.setRowCount(100)
        self.tableWidget_1.setColumnCount(3)
        self.tableWidget_1.setObjectName("tableWidget_1")
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_1.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_1.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_1.setHorizontalHeaderItem(2, item)
        self.tableWidget_1.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget_1.horizontalHeader().setHighlightSections(False)
        self.tableWidget_1.horizontalHeader().setSortIndicatorShown(False)
        self.tableWidget_1.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_1.verticalHeader().setVisible(False)
        self.tableWidget_1.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget_1.verticalHeader().setHighlightSections(False)
        self.pushButton_add = QtWidgets.QPushButton(self.frame_2)
        self.pushButton_add.setGeometry(QtCore.QRect(175, 160, 100, 30))
        self.pushButton_add.setStyleSheet("background-color:rgb(40, 176, 221);\n"
"border-radius: 10px;")
        self.pushButton_add.setObjectName("pushButton_add")
        self.verticalLayout.addWidget(self.frame_2)
        self.frame_3 = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy)
        self.frame_3.setMinimumSize(QtCore.QSize(0, 300))
        self.frame_3.setMaximumSize(QtCore.QSize(16777215, 300))
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setLineWidth(0)
        self.frame_3.setObjectName("frame_3")
        self.tableWidget_2 = QtWidgets.QTableWidget(self.frame_3)
        self.tableWidget_2.setGeometry(QtCore.QRect(0, 0, 450, 300))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget_2.sizePolicy().hasHeightForWidth())
        self.tableWidget_2.setSizePolicy(sizePolicy)
        self.tableWidget_2.setMinimumSize(QtCore.QSize(0, 300))
        self.tableWidget_2.setMaximumSize(QtCore.QSize(16777215, 300))
        self.tableWidget_2.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.tableWidget_2.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tableWidget_2.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_2.setRowCount(100)
        self.tableWidget_2.setColumnCount(4)
        self.tableWidget_2.setObjectName("tableWidget_2")
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(0, 0, item)
        self.tableWidget_2.horizontalHeader().setVisible(True)
        self.tableWidget_2.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget_2.horizontalHeader().setDefaultSectionSize(100)
        self.tableWidget_2.horizontalHeader().setHighlightSections(False)
        self.tableWidget_2.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_2.verticalHeader().setVisible(False)
        self.tableWidget_2.verticalHeader().setHighlightSections(False)
        self.verticalLayout.addWidget(self.frame_3)
        DownloadWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(DownloadWindow)
        QtCore.QMetaObject.connectSlotsByName(DownloadWindow)

    def retranslateUi(self, DownloadWindow):
        _translate = QtCore.QCoreApplication.translate
        DownloadWindow.setWindowTitle(_translate("DownloadWindow", "MainWindow"))
        self.lineEdit_1.setPlaceholderText(_translate("DownloadWindow", "请输入视频播放地址......"))
        item = self.tableWidget_1.horizontalHeaderItem(0)
        item.setText(_translate("DownloadWindow", "文件名"))
        item = self.tableWidget_1.horizontalHeaderItem(1)
        item.setText(_translate("DownloadWindow", "开始时间"))
        item = self.tableWidget_1.horizontalHeaderItem(2)
        item.setText(_translate("DownloadWindow", "结束时间"))
        self.pushButton_add.setText(_translate("DownloadWindow", "添加任务"))
        item = self.tableWidget_2.horizontalHeaderItem(0)
        item.setText(_translate("DownloadWindow", "文件名"))
        item = self.tableWidget_2.horizontalHeaderItem(1)
        item.setText(_translate("DownloadWindow", "视频地址"))
        item = self.tableWidget_2.horizontalHeaderItem(2)
        item.setText(_translate("DownloadWindow", "时间范围"))
        item = self.tableWidget_2.horizontalHeaderItem(3)
        item.setText(_translate("DownloadWindow", "进度"))
        __sortingEnabled = self.tableWidget_2.isSortingEnabled()
        self.tableWidget_2.setSortingEnabled(False)
        self.tableWidget_2.setSortingEnabled(__sortingEnabled)
import icons_rc
