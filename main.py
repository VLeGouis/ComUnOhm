import os
import sys

from PyQt5 import QtWidgets, QtSerialPort
from PyQt5.Qt import *
from PyQt5 import *

import Common
from Command import Command
from Logger import log
from MainWindow import *
import breeze_ressource


class MainWindow(QMainWindow, Ui_MainWindow):

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

        # Set dark theme by toggling
        self.theme = ":/light/stylesheet.qss"
        self.ToggleTheme()

        # Serial Port not opened for now
        self.ser = QtSerialPort.QSerialPort(
            readyRead=self.receive
        )

        self.list_cmd = list()
        self.AddCmd("Test1")  # debug
        self.AddCmd("Test2")  # debug

    def ConnectWidget(self):
        # Port Combo Box
        self.portCBox.currentTextChanged.connect(self.ConnectSerial)
        # Refresh port button
        self.refreshButton.clicked.connect(lambda: Common.GetSerial(self.portCBox))
        # Close port button
        self.opencloseButton.clicked.connect(self.ClosePort)
        # Change baudrate
        self.baudrateCBox.currentTextChanged.connect(self.ConnectSerial)
        # Add command button
        self.addCmdButton.clicked.connect(lambda: self.AddCmd())
        # Save button
        self.saveAction.triggered.connect(self.SaveFile)
        # Open File action
        self.openAction.triggered.connect(self.OpenFile)
        # Dark mode Action
        self.themeAction.triggered.connect(self.ToggleTheme)

    ##########################
    # Serial Port Management
    ##########################
    def ConnectSerial(self):
        port_name = self.portCBox.currentText()
        port_name = port_name.split(" -")[0]

        # TODO Ensure port is not already open with the new worker system

        if not port_name.startswith("Pas de port COM"):
            baudrate = int(self.baudrateCBox.currentText())

            self.ser.setPortName(port_name)
            self.ser.setBaudRate(baudrate, QSerialPort.AllDirections)
            self.ser.open(QSerialPort.ReadWrite)
            self.opencloseButton.setText("Fermer le port")
            self.opencloseButton.clicked.connect(self.ClosePort)
        else:
            self.ClosePort()

    def ClosePort(self):
        if self.ser.isOpen():
            self.ser.close()
            self.opencloseButton.setText("Ouvrir le port")
            self.opencloseButton.clicked.connect(self.ConnectSerial)


    @QtCore.pyqtSlot()
    def receive(self) -> None:
        text = bytearray(self.ser.readAll())
        self.logger.RxLog(bytearray(text))

    @QtCore.pyqtSlot(bytes)
    def Send(self, data) -> None:
        if self.ser.isOpen():
            self.ser.write(data)
        else:
            self.logger.Log("Pas de port COM ouvert", log.ERROR)



    ########################
    # Command section
    ########################
    def AddCmd(self, msg=""):
        pos = self.commandLayout.count() - 2
        cmd = Command(msg)
        cmd.deleteSignal.connect(self.DeleteCommand)
        cmd.sendSignal.connect(self.Send)
        self.list_cmd.append(cmd)
        self.commandLayout.insertWidget(pos, cmd)

    def DeleteCommand(self, wid2delete):
        wid2delete.deleteLater()
        self.commandLayout.removeWidget(wid2delete)

    """
    UI MANAGEMENT AND TIMING
    """

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F5:
            self.close()

    def closeEvent(self, event):
        print("Close event")
        if Common.serTh is not None:
            Common.serTh.running = False  # End serial thread

    def SaveFile(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(filter="(*.txt)")
        if filename:
            with open(filename, "w") as cmd_file:
                for cmd in self.list_cmd:
                    line = cmd.getCmd()
                    cmd_file.write(line + '\n')

            self.logger.Log(f"Log sauvegardé ici : {filename}", "green")

    def OpenFile(self):
        for cmd in self.list_cmd:
            self.DeleteCommand(cmd)

        self.list_cmd.clear()

        filename, _ = QFileDialog.getOpenFileName(filter="(*.txt)")

        if filename:
            try:
                # Get the lines of the file, on command per line
                with open(filename, "r+") as cmd_file:
                    cmds = cmd_file.readlines()
                    print(cmds)

                for cmd in cmds:
                    print(cmd)
                    self.AddCmd(cmd)

                self.logger.Log(f"Fichier chargé: {filename}", "green")

            except Exception as e:
                print(e)

    """
    Use self.theme attribut to toggle the graphic theme between light and dark
    
    @output Change self.theme path to the other theme
    """

    def ToggleTheme(self):
        if self.theme == ":/light/stylesheet.qss":
            self.theme = ":/dark/stylesheet.qss"
            self.themeAction.setText("Passer au thème lumineux")
        else:
            self.theme = ":/light/stylesheet.qss"
            self.themeAction.setText("Passer au thème sombre")

        file = QFile(self.theme)
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        QApplication.instance().setStyleSheet(stream.readAll())


def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


if __name__ == "__main__":
    sys._excepthook = sys.excepthook
    sys.excepthook = exception_hook
    # Execute the app
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
