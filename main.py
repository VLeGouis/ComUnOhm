import sys

from PyQt5 import QtWidgets
from PyQt5.Qt import *
from PyQt5.QtCore import QTimer

import Common
from Command import Command
from Logger import Logger, log
from MainWindow import *
from SerialManagement import SerialThread


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # uic.loadUi('MainWindow.ui', self)  # Load the .ui file
        self.setupUi(self)
        self.show()  # Show the GUI
        self.setWindowTitle("ComUnOhm")

        Common.init(self.logger)
        Common.GetSerial(self.portCBox)
        self.ConnectWidget()

        self.list_cmd = []
        self.AddCmd("Test")
        self.AddCmd("AT+Test")
        self.AddCmd("Delete TEST\r\n")

        # Serial
        self.last_frame = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.TimeoutUart)

    def ConnectWidget(self):
        # Port Combo Box
        self.portCBox.currentTextChanged.connect(lambda: self.ConnectSerial(self.portCBox.currentText()))
        # Refresh port button
        self.refreshButton.clicked.connect(lambda: Common.GetSerial(self.portCBox))
        # Add command button
        self.addCmdButton.clicked.connect(lambda: self.AddCmd())


    def ConnectSerial(self, port_name):
        try:
            port_name = port_name.split(" -")[0]
            if not port_name.startswith("Pas de port COM"):
                Common.serTh = SerialThread(port_name, 115200, self.logger)
                Common.serTh.start()
                Common.serTh.frameArrived.connect(self.logger.RxLog)
        except Exception as e:
            print(e)


    def AddCmd(self, msg=""):
        pos = self.commandLayout.count() - 2
        self.list_cmd.append(Command(msg))
        self.commandLayout.insertWidget(pos, self.list_cmd[-1])

    """
    UI MANAGEMENT AND TIMING
    """

    # Allow following if a timeout occur
    def TimeoutUart(self):
        self.last_frame.clear()
        self.timer.stop()
        self.logger.Log("Pas de réponse de la carte", log.ERROR)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F5:
            self.close()

    def closeEvent(self, event):
        print("Close event")
        Common.serTh.running = False
        Common.serTh.wait()


if __name__ == "__main__":
    import os  # Used in Testing Script
    os.system("pyuic5 MainWindow.ui -o MainWindow.py")
    os.system("pyuic5 command.ui -o CommandUi.py")
    os.system("pyuic5 Logger.ui -o LoggerUi.py")
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec_()
