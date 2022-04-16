from PyQt5 import QtCore, QtGui, QtWidgets
from LoggerUi import *
import Common
from Common import *


class log(Enum):
    TX = 1
    RX = 2
    ERROR = 3
    APPEND = 4


class Logger(QtWidgets.QWidget, Ui_Logger):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)

        self.new_frame = True

        self.logBrowser.setReadOnly(True)
        self.saveButton.clicked.connect(self.SaveLog)
        self.eraseButton.clicked.connect(self.EraseLog)

    def SaveLog(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(filter="(*.txt)")
        if filename:
            with open(filename, "w") as log_file:
                log_file.write(self.logBrowser.toPlainText())
            self.Log(f"Log sauvegardé ici : {filename}", "green")

    def EraseLog(self):
        self.logBrowser.clear()
        self.new_frame = True

    def Log(self, msg: str, args=0):

        line = '\r\n[' + datetime.now().strftime("%d/%m/%Y, %H:%M:%S") + '] '

        if args == log.TX:
            line = f"<span style=\"font-weight: bold;color:#9c0000;\"> {line} TX -> </span> " \
                   f"<span style=\"color:#9c0000;\">{msg}</span> "
            self.new_frame = True

        elif args == log.RX:
            line = f"<span style=\"font-weight: bold;color:#005300;\"> {line} RX -> </span> " \
                   f"<span style=\"color:#005300;\">{msg}</span> "
            self.new_frame = False

        elif args == log.APPEND:
            line = f"<span style=\"color:#005300;\">{msg}</span>"
            if msg==" ":
                self.logBrowser.insertPlainText(msg)
            else :
                self.logBrowser.insertHtml(line)
                self.logBrowser.update()
            return

        elif args == log.ERROR:
            print("error")
            color = matplotlib.colors.cnames["red"]
            line = f"<span style=\"font-weight: bold;color:{color};\" > {line} -> {msg}</span> "
            self.new_frame = True

        else:
            line = f"<span style=\"font-weight: bold; \"> {line} </span> {msg}"

        self.logBrowser.append(line)
        self.logBrowser.update()

    def RxLog(self, rxdata):
        if self.encodingCBox.currentText() == 'HEX':
            msg = ""
            for char in rxdata:
                msg += f"0x{char:02x} "
            self.Log(msg, log.RX)

        else:
            try:
                msg = rxdata.decode(self.encodingCBox.currentText())
                print(msg.encode())
                msg, appendix = self.GetAppendice(msg)
                print(self.new_frame, appendix)
                print(msg.encode())

                if self.new_frame or appendix:
                    self.Log(msg, log.RX)

                else:
                    self.Log(msg, log.APPEND)

            except Exception as e:
                print(e)
                self.Log("Un charactère non Ascii a été trouvé", log.ERROR)
                msg = ""
                for char in rxdata:
                    msg += f"0x{char:02x} "
                self.Log(msg, log.RX)

    def TxLog(self, txdata):
        if self.encodingCBox.currentText() == 'HEX':
            msg = ""
            for char in txdata:
                msg += f"0x{char:02x} "
            self.Log(msg, log.TX)

        else:
            try:
                self.Log(txdata.decode(self.encodingCBox.currentText()), log.TX)
            except:
                self.Log("Un charactère non Ascii a été trouvé", log.ERROR)
                msg = ""
                for char in txdata:
                    msg += f"0x{char:02x} "
                self.Log(msg, log.TX)

    def GetAppendice(self, msg: str):
        if self.crlfCBox.currentText() == "Pas de CR+LF" :
            return msg, False

        if msg.endswith("\r"):
            if self.crlfCBox.currentText() == "AUTO LF":
                return msg[:-1] + "\n", True
            if self.crlfCBox.currentText() == "AUTO CR+LF":
                return msg + "\n", True
            return msg, True

        if msg.endswith("\n"):

            if self.crlfCBox.currentText() == "AUTO CR":
                return msg[:-1] + "\r", True
            if self.crlfCBox.currentText() == "AUTO CR+LF":
                if not msg.endswith("\r\n"):
                    return msg[:-1] + "\r\n", True
            return msg, True

        else:

            if self.crlfCBox.currentText() == "AUTO LF":
                return msg + "\n", True
            if self.crlfCBox.currentText() == "AUTO CR":
                return msg + "\r", True
            if self.crlfCBox.currentText() == "AUTO CR+LF":
                print("No CRLF")
                return msg + "\r\n", True
            print(self.crlfCBox.currentText())
            return msg, False
