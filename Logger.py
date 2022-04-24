from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from LoggerUi import *
import Common
from Common import *


class Logger(QtWidgets.QWidget, Ui_Logger):
    sendSignal = QtCore.pyqtSignal(bytes)

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)

        # Needed to follow if the next line need a timing header
        self.next_fr_need_header = True

        self.logBrowser.setReadOnly(True)
        self.saveButton.clicked.connect(self.SaveLog)
        self.eraseButton.clicked.connect(self.clearLog)

        self.appendix = ""
        self.last_msg_was = "None"
        self.crlfCBox.currentTextChanged.connect(self.updateAppendix)


    def SaveLog(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(filter="(*.txt)")
        if filename:
            with open(filename, "w") as log_file:
                log_file.write(self.logBrowser.toPlainText())
            self.Log(f"Log sauvegardé ici : {filename}", "green")

    def clearLog(self):
        self.logBrowser.clear()
        self.next_fr_need_header = True

    """
    Logging function for RX and TX with colored input
    @input msg      String to display
    @input append   this determine if we need to display the timing header
    """

    def Log(self, msg, color="#f000", append=False, error=False, msg_type="None"):
        if error:
            color = "#FF0000"  # Red
            self.next_fr_need_header = True
        msg = msg.replace("\r", "<CR>").replace("\n", "<LF>")

        line = f"<span style=\"color:{color};\">{msg}</span>"

        if self.next_fr_need_header or msg_type != self.last_msg_was:
            header = '\r\n[' + datetime.now().strftime("%d/%m/%Y, %H:%M:%S") + ']'
            line = f"<span style=\"font-weight: bold;color:{color};\">{header}</span> {line}"
            self.logBrowser.append(line)

        else:
            if msg == " " : #Allow space to be displayed
                self.logBrowser.insertPlainText(" ")
            else :
                self.logBrowser.insertHtml(line)
            print(self.logBrowser.toPlainText())

        self.last_msg_was = msg_type
        self.logBrowser.update()

    def rxLog(self, data: bytes, header="RX", msg_type="rx", color="#009933"):

        if self.encodingCBox.currentText() == 'HEX':
            hexstring = "0x" + " 0x".join("{:02x}".format(c) for c in data)
            self.Log(f"{header} -> {hexstring}", msg_type=msg_type)

        else:
            try:
                msg = data.decode(self.encodingCBox.currentText())
            except:
                self.Log("Wrong char in msg for encoding", msg_type=msg_type)
                hexstring = "0x" + " 0x".join("{:02x}".format(c) for c in data)
                self.next_fr_need_header = True
                self.Log(f"{header} -> {hexstring}", msg_type=msg_type)
                return

            msg, appendix = self.getAppendix(msg)

            if self.next_fr_need_header:
                msg = f"{header} -> " + msg

            self.Log(msg, append=not self.next_fr_need_header, msg_type=msg_type, color=color)
            self.next_fr_need_header = appendix

    def txLog(self, txdata: bytes):
        self.rxLog(txdata, header="TX", msg_type="tx", color="#0066ff")

    def updateAppendix(self) -> None:
        if self.crlfCBox.currentText() == "Pas de CR+LF":
            self.appendix = ""
        elif self.crlfCBox.currentText() == "AUTO CR+LF":
            self.appendix = "\r\n"
        elif self.crlfCBox.currentText() == "AUTO CR":
            self.appendix = "\r"
        elif self.crlfCBox.currentText() == "AUTO LF":
            self.appendix = "\n"

    def getAppendix(self, msg: str):
        if self.appendix == "":
            return msg, (msg.endswith("\r\n") or msg.endswith("\n") or msg.endswith("\r"))

        cur_app = ""

        # First find the hypothetical CRLF
        if len(msg) >= 1:
            if msg[-1] == "\n":
                cur_app += "\n"

                if len(msg) >= 2 and msg[-2] == "\r":
                    cur_app = "\r\n"

            elif msg[-1] == "\r":
                cur_app = "\r"

        if cur_app is not self.appendix:
            msg = msg[:len(msg) - len(cur_app)] + self.appendix

        return msg, True

    def keyPressEvent(self, event):
        encoding = self.encodingCBox.currentText()

        if event.key() == Qt.Key_Backspace:
            self.sendSignal.emit("\b".encode(encoding))

        # TODO Make teh space key being catched
        if event.key() == Qt.Key_Space:
            print("space")
            self.sendSignal.emit(" ".encode(encoding))

        # TODO Make backspace catched in log with erasing last char

        if encoding == "ASCII":
            if event.text().isascii():
                self.sendSignal.emit(event.text().encode(encoding))
            else:
                self.Log("Encodage de ce charactère impossible")

        elif event.key() == Qt.Key_Return:
            self.sendSignal.emit("\r\n".encode(encoding))

        else:
            try:
                self.sendSignal.emit(event.text().encode(encoding))
            except:
                self.Log("Encodage de cette touche impossible")
