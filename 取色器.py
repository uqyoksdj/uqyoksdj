import os

import PyQt5
from PyQt5.QtWidgets import QApplication, QColorDialog, QMainWindow, QPushButton

class ColorPickerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 Color Picker Example'
        self.width = 200
        self.height = 100
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, self.width, self.height)

        self.colorButton = QPushButton('Choose Color', self)
        self.colorButton.setGeometry(30, 30, 110, 40)
        self.colorButton.clicked.connect(self.chooseColor)

    def chooseColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.colorButton.setStyleSheet('background-color: %s' % color.name())

def main():
    app = QApplication([])
    ex = ColorPickerApp()
    ex.show()
    app.exec_()

if __name__ == '__main__':
    dirname = os.path.dirname(PyQt5.__file__)
    qt_dir = os.path.join(dirname, 'Qt5', 'plugins', 'platforms')
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_dir
    main()