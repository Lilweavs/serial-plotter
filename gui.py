from os import error
from typing import TypeGuard
from PyQt5 import QtCore, QtGui, QtWidgets, QtSerialPort
from PyQt5.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QPushButton, QWidget, QTextBrowser, QGridLayout, QLineEdit, QComboBox
import sys
from serial.serialwin32 import Serial
from serial.tools import list_ports
from serial.serialutil import SerialException
import serial
from threading import Thread, current_thread
from queue import Queue


class SerialPort(QtCore.QObject):
    port  = 'COM1'
    baudRate = 9600
    def __init__(self, q: Queue, parent = None) -> None:
        super().__init__(parent)
        self.msg = q
    # Explicit Signal
    # dataReady = QtCore.pyqtSignal(str)

    # @QtCore.pyqtSlot(str)
    def startSerialCommunication(self):
        stop = current_thread()
        with serial.Serial(self.port, self.baudRate, timeout=1) as ser:
            print('Connected')
            ser.reset_input_buffer()
            while getattr(stop, "do_run", True):
                line = ser.readline()
                line = line.decode('ascii')
                self.msg.put(line)
                # self.dataReady.emit(line)

class GUI(QMainWindow):
    """Main Window"""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('Serial Monitor')
        self.mainWidget = QWidget(self)
        self.setCentralWidget(self.mainWidget)

        self.msg = Queue()

        """Initialize All Qt Widgets"""
        self.sendButton         = QPushButton('Send')
        self.serialInputBrowser = QPlainTextEdit()
        self.serialInputEditor  = QLineEdit()
        self.baudRateMenu       = QComboBox()
        self.openSerialButton   = QPushButton('Connect')
        self.comPortMenu        = QComboBox()

        """ASCII Browser Settings And Parameters"""
        self.serialInputBrowser.setMaximumBlockCount(500) # Limits Text Log to 500 lines of text
        self.scrollBar = self.serialInputBrowser.verticalScrollBar()
        self.scrollBar.setValue(self.scrollBar.maximum())

        """Layout Widgets In GUI Window"""
        layout = QGridLayout()
        layout.addWidget(self.comPortMenu, 0, 0)
        layout.addWidget(self.baudRateMenu, 0, 1)
        layout.addWidget(self.openSerialButton, 0, 2)
        layout.addWidget(self.serialInputBrowser, 1, 0, 1, 3)
        layout.addWidget(self.serialInputEditor, 2, 0, 2, 2)
        layout.addWidget(self.sendButton, 2, 2)
        self.mainWidget.setLayout(layout)

        """Com Port Menu Settings And Parameters"""
        for port in list_ports.comports():
            print(port.description)
            self.comPortMenu.addItem(port.device)
        self.comPortMenu.currentTextChanged.connect(self.setComPort)

        """Connect Button Settings And Parameters"""
        self.openSerialButton.clicked.connect(self.openSerialPort)

        """Send Button Settings And Parameters"""
        self.sendButton.clicked.connect(self.sendButtonHandler)

        """Serial Input Browser Settings And Parameters"""
        self.serialInputBrowser.setReadOnly(True)

        """Baud Rate Menu Settings And Paremters"""
        self.baudRateMenu.addItems(['9600', '19200', '38400', '115200'])
        self.baudRateMenu.currentTextChanged.connect(self.setBaudRate)

        """Serial Object Settings"""

    

    def sendButtonHandler(self, e):
        self.serialInputBrowser.insertPlainText(self.serialInputEditor.text())
        self.serialInputEditor.clear()

    def setBaudRate(self, e):
        self.baudrate = int(e)
        print("BaudRate: ", int(e))

    def setComPort(self, e):
        self.port = e
        print("Port: ", e)

    def openSerialPort(self, e):
        if self.openSerialButton.text() == "Connect":
            try:
                self.device = SerialPort(self.msg)
                self.device.port = self.port
                self.device.baudRate = self.baudrate
                # self.device.dataReady.connect(self.textWindowHandler)

                self.timer = QtCore.QTimer()
                self.timer.setInterval(1000//30)
                self.timer.timeout.connect(self.textWindowHandler)
                self.timer.start()

                self.serialThread = Thread(target=self.device.startSerialCommunication)
                self.serialThread.daemon = True

                self.serialThread.start()
                # self.textThread.start()

            except SerialException as err:
                print(err)
                return
            self.openSerialButton.setText('Disconnect')
        else:
            self.openSerialButton.setText('Connect')
            self.serialThread.do_run = False
            self.timer.stop()
            # self.textThread.do_run = False

    def textWindowHandler(self):

        print(self.msg.qsize())
        for i in range(self.msg.qsize()):
            self.serialInputBrowser.insertPlainText(self.msg.get())
        self.scrollBar.setValue(self.scrollBar.maximum())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec_())
