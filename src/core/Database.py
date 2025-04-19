import os
import sys
import sqlite3
import json

import PyQt5
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLineEdit, QMessageBox, QCheckBox, QFileDialog, QHeaderView,
                             QAbstractItemView)


class DatabaseApp(QWidget):
    closed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.loadData()

    def initUI(self):
        self.setWindowTitle('数据库')
        self.setFixedWidth(800)

        self.layout = QVBoxLayout()

        self.tableWidget = QTableWidget()
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        horizontal_header = self.tableWidget.horizontalHeader()
        horizontal_header.setSectionResizeMode(QHeaderView.Stretch)

        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(['文件名', '视频地址', '开始时间', '结束时间'])
        self.layout.addWidget(self.tableWidget)

        self.input_layout = QHBoxLayout()
        self.file_name_input = QLineEdit(self)
        self.file_name_input.setPlaceholderText('文件名')
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText('视频地址')
        self.start_time_input = QLineEdit(self)
        self.start_time_input.setPlaceholderText('开始时间')
        self.end_time_input = QLineEdit(self)
        self.end_time_input.setPlaceholderText('结束时间')

        self.input_layout.addWidget(self.file_name_input)
        self.input_layout.addWidget(self.url_input)
        self.input_layout.addWidget(self.start_time_input)
        self.input_layout.addWidget(self.end_time_input)

        self.layout.addLayout(self.input_layout)

        self.modify_checkbox = QCheckBox("勾选开启修改模式")
        self.modify_checkbox.stateChanged.connect(self.toggleModifications)
        self.layout.addWidget(self.modify_checkbox)

        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton('添加')
        self.add_button.clicked.connect(self.addRecord)
        self.add_button.setEnabled(False)
        self.update_button = QPushButton('修改')
        self.update_button.clicked.connect(self.updateRecord)
        self.update_button.setEnabled(False)
        self.delete_button = QPushButton('删除')
        self.delete_button.clicked.connect(self.deleteRecord)
        self.delete_button.setEnabled(False)
        self.query_button = QPushButton('查询')
        self.query_button.clicked.connect(self.queryRecord)
        self.refresh_button = QPushButton('刷新')
        self.refresh_button.clicked.connect(self.loadData)
        self.export_button = QPushButton('导出')
        self.export_button.clicked.connect(self.exportToJson)

        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.update_button)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addWidget(self.query_button)
        self.button_layout.addWidget(self.refresh_button)
        self.button_layout.addWidget(self.export_button)

        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)

    def loadData(self):
        connection = sqlite3.connect("data/data.db")
        result = connection.execute("SELECT * FROM record")

        # 获取查询结果的列数
        columns = len(result.description) - 1
        # 重置表格状态，清除旧数据
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(columns)  # 根据需要设置列数

        self.tableWidget.setHorizontalHeaderLabels(['文件名', '视频地址', '开始时间', '结束时间'])

        for row_number, row_data in enumerate(result):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data[1:], start=1):
                self.tableWidget.setItem(row_number, column_number - 1, QTableWidgetItem(str(data)))

        connection.close()

    def addRecord(self):
        if not self.modify_checkbox.isChecked():
            return

        file_name = self.file_name_input.text()
        url = self.url_input.text()
        start_time = self.start_time_input.text()
        end_time = self.end_time_input.text()

        if self.checkInputs():
            connection = sqlite3.connect("data/data.db")
            cursor = connection.cursor()
            cursor.execute("INSERT INTO record (file_name, url, start_time, end_time) VALUES (?, ?, ?, ?)",
                           (file_name, url, start_time, end_time))
            connection.commit()
            connection.close()

            self.clearInputs()
            self.loadData()
        self.clearInputs()

    def updateRecord(self):
        if not self.modify_checkbox.isChecked():
            return

        selected_row = self.tableWidget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, '警告', '没有选择行')
            return

        record_id = self.tableWidget.item(selected_row, 0).text()
        file_name = self.file_name_input.text()
        url = self.url_input.text()
        start_time = self.start_time_input.text()
        end_time = self.end_time_input.text()

        if self.checkInputs():
            connection = sqlite3.connect("data/data.db")
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE record 
                SET file_name = ?, url = ?, start_time = ?, end_time = ? 
                WHERE id = ?
            """, (file_name, url, start_time, end_time, record_id))
            connection.commit()
            connection.close()

            self.clearInputs()
            self.loadData()
        self.clearInputs()

    def deleteRecord(self):
        if not self.modify_checkbox.isChecked():
            return

        selected_row = self.tableWidget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, '警告', '没有选择行')
            return

        reply = QMessageBox.question(self, '确认删除',
                                     '你确定要删除这条记录？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            record_id = self.tableWidget.item(selected_row, 0).text()

            connection = sqlite3.connect("data/data.db")
            cursor = connection.cursor()
            cursor.execute("DELETE FROM record WHERE id = ?", (record_id,))
            connection.commit()
            connection.close()

            self.loadData()

    def queryRecord(self):
        file_name = self.file_name_input.text()
        url = self.url_input.text()
        start_time = self.start_time_input.text()
        end_time = self.end_time_input.text()

        query = "SELECT * FROM record WHERE 1=1"
        params = []
        if file_name:
            query += " AND file_name = ?"
            params.append(file_name)
        if url:
            query += " AND url = ?"
            params.append(url)
        if start_time:
            query += " AND start_time = ?"
            params.append(start_time)
        if end_time:
            query += " AND end_time = ?"
            params.append(end_time)

        connection = sqlite3.connect("data/data.db")
        result = connection.execute(query, params)
        self.tableWidget.setRowCount(0)

        for row_number, row_data in enumerate(result):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        connection.close()

    def exportToJson(self):
        path, _ = QFileDialog.getSaveFileName(self, "保存文件", "", "JSON Files (*.json)")
        if path:
            data = []
            for row in range(self.tableWidget.rowCount()):
                record = {
                    "file_name": self.tableWidget.item(row, 1).text(),
                    "url": self.tableWidget.item(row, 2).text(),
                    "start_time": self.tableWidget.item(row, 3).text(),
                    "end_time": self.tableWidget.item(row, 4).text()
                }
                data.append(record)
            with open(path, 'w') as file:
                json.dump(data, file, indent=4)

    def checkInputs(self):
        if (self.file_name_input.text() and self.url_input.text() and
                self.start_time_input.text() and self.end_time_input.text()):
            return True
        else:
            return False

    def clearInputs(self):
        self.file_name_input.clear()
        self.url_input.clear()
        self.start_time_input.clear()
        self.end_time_input.clear()

    def toggleModifications(self):
        if self.modify_checkbox.isChecked():
            self.add_button.setEnabled(True)
            self.update_button.setEnabled(True)
            self.delete_button.setEnabled(True)
        else:
            self.add_button.setEnabled(False)
            self.update_button.setEnabled(False)
            self.delete_button.setEnabled(False)

    def closeEvent(self, event):
        self.closed.emit(1)
        event.accept()


if __name__ == '__main__':
    dirname = os.path.dirname(PyQt5.__file__)
    qt_dir = os.path.join(dirname, 'Qt5', 'plugins', 'platforms')
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_dir

    app = QApplication(sys.argv)
    ex = DatabaseApp()
    ex.show()
    sys.exit(app.exec_())
