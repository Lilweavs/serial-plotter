import re
import sys

import qdarkstyle
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QAbstractButton, QApplication, QMainWindow
from PyQt5.uic import loadUi
from serial.tools import list_ports

from SerialMonitor_ui import Ui_MainWindow
from SerialPort import SerialThread


def str2hex(data):
    return " ".join(["%02X" % ord(b) for b in data])

def hex2str(data):
    return " ".join([f"{b:02x}" for b in data]).upper()

class Window(QMainWindow, Ui_MainWindow):

    displayMode = "ASCII"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.device = SerialThread()
        self.setupUi(self)
        self.setupSignalsAndSlots()

    def setupSignalsAndSlots(self):
        self.buttonConnect.clicked.connect(self._SerialConnect)
        self.buttonClear.clicked.connect(self._ClearDisplay)    

        for port in list_ports.comports():
            self.comboBoxPort.addItem(port.device)
        self.comboBoxPort.currentTextChanged.connect(self._SetPort)
        self.device.comPort = self.comboBoxPort.currentText()

        for baud in ("9600", "19200", "38400", "57600", "115200", "921600"):
            self.comboBoxBaudrate.addItem(baud)
        self.comboBoxBaudrate.currentTextChanged.connect(self._SetBaudRate)

        self.comboBoxSerialEnd.currentTextChanged.connect(self._SetSerialEnd)

        self.buttonGroupParity.buttonClicked.connect(self._SetParity)
        self.buttonGroupDataBits.buttonClicked.connect(self._SetDataBits)
        self.buttonGroupDisplay.buttonClicked.connect(self._SetDisplayCfg)
        self.buttonGroupHFC.buttonClicked.connect(self._SetHFC)
        self.buttonGroupSFC.buttonClicked.connect(self._SetSFC)
        self.buttonGroupStopBits.buttonClicked.connect(self._SetStopBits)
        
        self.device.status.connect(self._SerialStarted)

        self.plainTextEditSerialViewer.setMaximumBlockCount(500) # Limits Text Log to 500 lines of text
        self.scrollBar = self.plainTextEditSerialViewer.verticalScrollBar()
        self.scrollBar.setValue(self.scrollBar.maximum())

    def updateStatusBar(self, s: str, timeout: int=0):
        self.statusbar.showMessage(s, timeout)
        self.statusbar.repaint()
    
    def _SetPort(self, event):
        self.device.comPort = str(event)
        print(str(event))

    def _SetBaudRate(self, event):
        self.device.baudRate = int(event)
        print(str(event))

    def _SetSerialEnd(self, event):
        if str(event) == "None":
            self.device.endChar = ''
        else:
            self.device.endChar = str(event)
        print(str(event))

    def _SerialStarted(self, status: int, err: str):
        if not status:
            self.buttonConnect.setText("Disconnect")
            self.updateStatusBar(f"Connected: {self.device.comPort} @ {self.device.baudRate}")

            self.timer = QTimer()
            self.timer.setInterval(1000//30)
            self.timer.timeout.connect(self.textWindowHandler)
            self.timer.start()

        else:
            self.buttonConnect.setText("Connect")
            self.updateStatusBar(f"Failed: {err}")

    def _SerialConnect(self, event):
        if self.buttonConnect.text() == "Connect":
            self.device.start()
        else:
            self.buttonConnect.setText("Connect")
            self.device.running = False # Probably doesn't matter if thread safe or not. Worst case, get old value?
            self.device.wait()
            self.timer.stop()

            self.updateStatusBar("Port Closed", 2000)

    def _SetParity(self, event):
        self.device.parity = self.device.PARITY[event.text()]
        print(str(event.text()))

    def _SetDataBits(self, event):
        self.device.databit = self.device.DATABIT[event.text()]
        print(str(event.text()))

    def _ClearDisplay(self, event):
        self.plainTextEditSerialViewer.clear()

    def _SetDisplayCfg(self, event):
        ckdBtn = self.sender().checkedButton().text()

        if ckdBtn == self.displayMode:
            return
        
        if ckdBtn == "HEX":
            self.displayMode = ckdBtn
            tmp = str2hex(self.plainTextEditSerialViewer.toPlainText())
        else:
            self.displayMode = ckdBtn
            tmp = bytearray.fromhex(self.plainTextEditSerialViewer.toPlainText()).decode()
    
        self.plainTextEditSerialViewer.clear()
        self.plainTextEditSerialViewer.insertPlainText(tmp)

    def _SetHFC(self, event):
        if event.text() == "RTS/CTS":
            self.device.dsrdtr = False
            self.device.rtscts = True
        elif event.text() == "DSR/DTR":
            self.device.rtscts = False
            self.device.dsrdtr = True
        else:
            self.device.dsrdtr = False
            self.device.rtscts = False

        print(str(event.text()))

    def _SetSFC(self, event):
        if event.text() == "On":
            self.device.xonxoff = True
        else:
            self.device.xonxoff = False
        print(str(event.text()))

    def _SetStopBits(self, event):
        self.device.stopbit = self.device.STOPBITS[event.text()]
        print(str(event.text()))

    def textWindowHandler(self):
        if self.device.rxq.qsize():
            size = self.device.rxq.qsize()
            for i in range(size):
                if self.displayMode == "ASCII":
                    self.plainTextEditSerialViewer.insertPlainText(self.device.rxq.get())
                else:
                    # self.plainTextEditSerialViewer.insertPlainText(str2hex(self.device.rxq.get()))
                    self.plainTextEditSerialViewer.insertPlainText(f"{hex2str(self.device.rxq.get())} ")
                    
                if self.scrollBar.value() + 4 >= (self.scrollBar.maximum()):
                    self.scrollBar.setValue(self.scrollBar.maximum())



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    win.show()
    sys.exit(app.exec())
