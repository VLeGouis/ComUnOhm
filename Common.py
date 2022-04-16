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

    os.system("pyuic5 MainWindow.ui -o MainWindow.py")


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
            combo_box.addItem(f"{port.name} - {port.description}")
        return True
        # Try to connect in order








def CleanHexInput(text_input: str):
    # Clean data of prefix, LF and space
    text_input = text_input.replace(' ', '') \
        .replace('0x', '') \
        .replace('0X', '') \
        .replace('$', '') \
        .replace('\n', '') \
        .replace(',', '')

    # Check for odd char
    if not all(c in string.hexdigits for c in text_input):
        print(text_input)
        Log("Données de test non reconnues comme format hexadécimal", "red")
        return False, []

    # Check parity
    if len(text_input) % 2:
        Log("Merci d'écrire les données sous forme de paire de caractère hexadécimaux. ", "red")
        return False, []

    # Check len
    if len(text_input) == 0:
        Log("Merci d'écrire les données de la trame de test", "red")
        return False, []

    Log("Donnée de test acceptées", "green")
    # Convert to int
    test_data = [text_input[i:i + 2] for i in range(0, len(text_input), 2)]
    test_data = list(map(lambda it: int(it, 16), test_data))

    return True, test_data
