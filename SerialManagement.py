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
        print(f"Init serial thread {self.portname} ")

    def write(self, data):  # Write outgoing data to serial port if open
        self.txq.put(data)  # ..using a queue to sync with reader thread

    def run(self):  # Run serial reader thread
        try:
            self.logger.Log(f"Ouverture du port {self.portname} au débit de {self.baudrate} bps")

            self.ser = serial.Serial(self.portname, self.baudrate, timeout=0.5)
            self.ser.flushInput()
        except Exception as e:
            print(f"Opening {e}")

        while self.running:

            # Read RX data
            if self.ser.in_waiting:
                rxdata = self.ser.read(self.ser.in_waiting)
                self.frameArrived.emit(rxdata)

            # If Tx data in queue, write to serial port
            if not self.txq.empty():
                txdata = self.txq.get()
                self.logger.TxLog(txdata)
                try:
                    self.ser.write(txdata)
                except Exception as e:
                    print(e)

            self.usleep(100)  # Release processor since everything is already buffered

        # Close serial port when thread finished
        self.close()

        print("finished")

    def close(self):
        if self.ser is not None :
            if self.ser.is_open:
                self.ser.close()
            self.ser = None
            print(f"close thread {self.portname}")
