from Common import *
from PyQt5 import QtCore
import queue as Queue


# Thread to handle incoming & outgoing serial data
class SerialThread(QtCore.QThread):
    frameArrived = QtCore.pyqtSignal(bytes)

    def __init__(self, portname: str, baudrate: int, log_widget: Logger):  # Initialise with serial port details
        QtCore.QThread.__init__(self)
        self.portname, self.baudrate = portname, baudrate
        self.txq = Queue.Queue()
        self.running = True
        self.ser = None
        self.logger = log_widget
        print("Init serial thread")

    def write(self, data):  # Write outgoing data to serial port if open
        self.txq.put(data)  # ..using a queue to sync with reader thread

    def run(self):  # Run serial reader thread

        try:
            self.ser.close()
        except Exception as e:
            pass

        try:
            self.logger.Log(f"Ouverture du port {self.portname} au débit de {self.baudrate} bps")
            self.ser = serial.Serial(self.portname, self.baudrate, timeout=0.5)
            self.ser.flushInput()

        except Exception as e:
            self.ser = None
            self.running = False
            print(f" run : {e} ")

        while self.running:

            # Read RX data
            if self.ser.in_waiting:
                rxdata = self.ser.read(self.ser.in_waiting)
                self.frameArrived.emit(rxdata)

            if not self.txq.empty():
                try:
                    txdata = self.txq.get()  # If Tx data in queue, write to serial port
                    self.logger.TxLog(txdata)
                    self.ser.write(txdata)
                except Exception as e:
                    print(e)
            self.usleep(100)  # Release processor since everything is already buffered

        if self.ser:  # Close serial port when thread finished
            self.ser.close()
            self.ser = None
