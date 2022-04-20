import os
from datetime import datetime

import serial
import serial.tools.list_ports
import matplotlib.colors
from PyQt5 import QtWidgets
import string

from enum import Enum

from Logger import Logger


def init(log_widget: Logger):
    global LogWidget
    LogWidget = log_widget

    global serTh
    serTh = None

def GetSerial(combo_box: QtWidgets.QComboBox) -> bool:
    combo_box.clear()
    combo_box.addItem("Pas de port COM")
    ports = serial.tools.list_ports.comports()

    if len(ports) == 0:
        LogWidget.Log("Pas de port COM", "red")
        return False  # No COM port where opened

    else:
        LogWidget.Log(f"{len(ports)} port{'s'[:(1 > 1)]} COM découvert")

        for port in ports:
            try :
                ser = serial.Serial(port.name)
                print(f"port {port.name} is open : {ser.is_open}")
                combo_box.addItem(f"{port.name} - {port.description}")
            except Exception as e:
                print(e)
                pass

        return True
        # Try to connect in order


