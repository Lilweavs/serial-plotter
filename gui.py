from os import error
from typing import TypeGuard
from PyQt5 import QtCore, QtGui, QtWidgets, QtSerialPort
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QMenuBar, QPlainTextEdit, QPushButton, QWidget, QTextBrowser, QGridLayout, QLineEdit, QComboBox
import sys
from serial.serialwin32 import Serial
from serial.tools import list_ports
from serial.serialutil import SerialException
import typing
import serial
from threading import Thread, current_thread
from queue import Queue


class SerialPort(QtCore.QObject):
    port  = 'COM1'
    baudRate = 9600
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        
    # Explicit Signal
    dataReady = QtCore.pyqtSignal(str)

    @QtCore.pyqtSlot(str)
    def startSerialCommunication(self):
        stop = current_thread()
        with serial.Serial(self.port, self.baudRate, timeout=1) as ser:
            print('Connected')
            ser.reset_input_buffer()
            while getattr(stop, "do_run", True):
                line = ser.readline()
                line = line.decode('ascii')
                self.dataReady.emit(line)

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
        # self.device = SerialPort()
        # self.device.port = 'COM1'
        # self.device.baudRate = 9600
        # self.device = serial.Serial()
        # self.device.port = 'COM1'
        # self.device.baudrate = 9600
        # self.device = QtSerialPort.QSerialPort()
        # self.device.setPortName('COM4')
        # self.device.setBaudRate(QtSerialPort.QSerialPort.Baud115200)
        # self.device.readyRead.connect(self.textWindowHandler)
        # self.connected = False

        # self.dataReady = QtCore.pyqtSignal(str)
        # self.dataReady.connect(self.textWindowHandler)
    

    def sendButtonHandler(self, e):
        # print(self.serialInputEditor.text())

        # txt = [hex(ord(x)) for x in self.serialInputEditor.text()]
        # txt = ' '.join(txt)
        self.serialInputBrowser.insertPlainText(self.serialInputEditor.text())
        # self.serialInputBrowser.append(self.serialInputEditor.text())
        # self.serialInputEditor.inputPlainText(txt)
        self.serialInputEditor.clear()

    def setBaudRate(self, e):
        self.baudrate = int(e)
        # self.device.setBaudRate(QtSerialPort.QSerialPort.Baud115200)
        print("BaudRate: ", int(e))

    def setComPort(self, e):
        self.port = e
        # self.device.setPortName(e)
        print("Port: ", e)

    def openSerialPort(self, e):
            # self.serialThread = QtCore.QThread()
            # self.device.moveToThread(self.serialThread)
            # self.device.dataReady.connect(self.serialThread.quit)
            # self.serialThread.started.connect(self.device.startSerialCommunication)
            # self.serialThread.start()
            # self.connected = True
        if self.openSerialButton.text() == "Connect":
            try:
                # self.textThread = Thread(target=self.textWindowHandler)
                # self.textThread.daemon = True
                self.device = SerialPort()
                self.device.port = self.port
                self.device.baudRate = self.baudrate
                self.device.dataReady.connect(self.textWindowHandler)
                
                # self.dataReady.connect(self.textWindowHandler)
                # self.textThread = QtCore.QThread()
                # self.textThread.start()
                # self.textThread.started.connect(self.textWindowHandler)
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
            # self.textThread.do_run = False

    def textWindowHandler(self, data):
        # print(data)
        self.serialInputBrowser.insertPlainText(data)
        self.serialInputEditor.verticalScrollBar().maximum()
        # dataReady = QtCore.pyqtSignal(str)
        # stop = current_thread()
        # # while getattr(stop, "do_run", True):
        # while getattr(stop, "do_run", True):
        #     if not self.msg.empty():
        #         line = self.msg.get(0)
        #         self.msg.task_done()
        #         self.dataReady.emit(line)


        #         self.serialInputBrowser.insertPlainText(line)
        #         print(line)
        
                # self.serialInputBrowser.verticalScrollBar().maximum()
                    # print(line)

    # def startSerialCommunication(self):
        
    #     try:
    #         stop = current_thread()
    #         self.device.open()
    #         print('Connected!')
    #         while getattr(stop, "do_run", True):
    #             line = self.device.readline()
    #             s = line.decode('ascii')
    #             self.msg.put(s)

    #     except SerialException as err:
    #         print(err)

    #     self.device.close()
    #     print('Disconnected!')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec_())
