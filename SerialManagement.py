from Common import *
from PyQt5 import QtCore
import queue as Queue


# Thread to handle incoming & outgoing serial data
class SerialThread(QtCore.QThread):
    frameArrived = QtCore.pyqtSignal(bytes)

    def __init__(self, log_widget: Logger):  # Initialise with serial port details
        QtCore.QThread.__init__(self)
        self.txq = Queue.Queue()
        self.running = True
        self.ser = None
        self.logger = log_widget
        print(f"Init serial thread ")

    def write(self, data):  # Write outgoing data to serial port if open
        self.txq.put(data)  # ..using a queue to sync with reader thread

    def run(self):
        self.running = True  # Run until stopped

        while self.running:
            if self.ser is None:
                self.msleep(100)  # Release processor since no port is open

            else:
                # Read RX data
                if self.ser.in_waiting:
                    rx_data = self.ser.read(self.ser.in_waiting)
                    self.frameArrived.emit(rx_data)

                # If Tx data in queue, write to serial port
                if not self.txq.empty():
                    tx_data = self.txq.get()
                    self.logger.TxLog(tx_data)
                    try:
                        self.ser.write(tx_data)
                    except Exception as e:
                        print(e)

                self.usleep(100)  # Release processor since everything is already buffered by the OS

    def ClosePort(self):
        if self.ser is not None:

            if self.ser.is_open:
                self.ser.close()
            print(f"Closed port")
            self.ser = None

    def OpenPort(self, portname: str, baudrate: int):
        try:
            self.ClosePort()  # Try to close it if ser already defined

            self.logger.Log(f"Ouverture du port {portname} au débit de {baudrate} bps")
            self.ser = serial.Serial(portname, baudrate, timeout=0.5)
            self.ser.flushInput()

        except Exception as e:
            print(f"open port {e}")

