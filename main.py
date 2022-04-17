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

        self.setupUi(self)
        self.show()  # Show the GUI
        self.setWindowTitle("ComUnOhm")

        # This part is to share the same log output from different files
        Common.init(self.logger)
        # Should be in dedicated file to get Serial Port
        Common.GetSerial(self.portCBox)

        # Init widget signal and connexion
        self.ConnectWidget()

        self.list_cmd = list()
        self.AddCmd("Test1")
        self.AddCmd("Test2")


    def ConnectWidget(self):
        # Port Combo Box
        self.portCBox.currentTextChanged.connect(lambda: self.ConnectSerial(self.portCBox.currentText()))
        # Refresh port button
        self.refreshButton.clicked.connect(lambda: Common.GetSerial(self.portCBox))
        # Add command button
        self.addCmdButton.clicked.connect(lambda: self.AddCmd())
        # Save button
        self.saveAction.triggered.connect(self.SaveFile)
        # Open File action
        self.openAction.triggered.connect(self.OpenFile)

    def ConnectSerial(self, port_name):
        try:
            port_name = port_name.split(" -")[0]
            if not port_name.startswith("Pas de port COM"):
                baudrate = int(self.baudrateCBox.currentText())
                Common.serTh = SerialThread(port_name, baudrate, self.logger)
                Common.serTh.start()
                Common.serTh.frameArrived.connect(self.logger.RxLog)

        except Exception as e:
            self.logger.Log(e, log.ERROR)

    def AddCmd(self, msg=""):
        pos = self.commandLayout.count() - 2
        cmd = Command(msg)
        cmd.deleteSignal.connect(self.DeleteCommand)
        self.list_cmd.append(cmd)
        self.commandLayout.insertWidget(pos, cmd)

    def DeleteCommand(self, wid2delete):
        self.commandLayout.removeWidget(wid2delete)

    """
    UI MANAGEMENT AND TIMING
    """

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F5:
            self.close()

    def closeEvent(self, event):
        print("Close event")
        Common.serTh.running = False
        Common.serTh.wait()

    def SaveFile(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(filter="(*.txt)")
        if filename:
            with open(filename, "w") as cmd_file:
                for cmd in self.list_cmd :
                    line = cmd.getCmd()
                    cmd_file.write(line+'\n')

            self.logger.Log(f"Log sauvegardé ici : {filename}", "green")

    def OpenFile(self):
        index = self.commandLayout.count()
        while (index >= 0):
            try :
                #Try to delete command from layout
                self.commandLayout.itemAt(index).widget().Delete()
                self.commandLayout.itemAt(index).widget().setParent(None)

            except Exception as e :
                print(e)
            index -= 1

        self.list_cmd.clear()

        filename, _ = QtWidgets.QFileDialog.getOpenFileNames(filter="(*.txt)")
        filename = filename[0]
        print(filename)
        if filename:
            try :
                #Get the lines of the file, on command per line
                with open(filename, "r+") as cmd_file:
                    cmds = cmd_file.readlines()
                    print(cmds)

                for cmd in cmds:
                    print(cmd)
                    self.AddCmd(cmd)

                self.logger.Log(f"Fichier chargé: {filename}", "green")

            except Exception as e :
                print(e)

if __name__ == "__main__":
    import os  # Used in Testing Script

    os.system("pyuic5 MainWindow.ui -o MainWindow.py")
    os.system("pyuic5 command.ui -o CommandUi.py")
    os.system("pyuic5 Logger.ui -o LoggerUi.py")
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec_()
