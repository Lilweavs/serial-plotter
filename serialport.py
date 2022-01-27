from queue import Queue

from BinaryParser import BinaryParser

from PyQt5.QtCore import QThread, pyqtSignal
from serial import (EIGHTBITS, FIVEBITS, PARITY_EVEN, PARITY_MARK, PARITY_NONE,
                    PARITY_ODD, PARITY_SPACE, SEVENBITS, SIXBITS, STOPBITS_ONE,
                    STOPBITS_TWO, Serial)
from serial.serialutil import SerialException


# Return hexadecimal values of data
def hexdump(data):
    return " ".join(["%02X" % ord(b) for b in data])

def hex2str(data):
    return " ".join([f"{b:02x}" for b in data]).upper()





class SerialThread(QThread):
    """ Class to Handle Serial Communication"""
    status = pyqtSignal(int,str)

    PARITY = {"None": PARITY_NONE,
              "Even": PARITY_EVEN,
              "Odd": PARITY_ODD,
              "Mark": PARITY_MARK,
              "Space": PARITY_SPACE}

    DATABIT = {"Eight": EIGHTBITS,
            "Seven": SEVENBITS,
            "Six": SIXBITS,
            "Five": FIVEBITS}

    STOPBITS = {"1 Bit": STOPBITS_ONE,
                "2 Bit": STOPBITS_TWO}

    def __init__(self, comPort: str=None, baudRate: int=9600) -> None:
        super().__init__()
        self.comPort  = comPort
        self.baudRate = baudRate
        self.parity   = PARITY_NONE
        self.stopbit  = STOPBITS_ONE
        self.databit  = EIGHTBITS
        self.timeout  = None
        self.xonxoff  = False
        self.rtscts   = False
        self.dsrdtr   = False
    
        self.endChar  = ''
        self.rxq      = Queue()
        self.running  = False
        self.binary   = True
        self.parser   = BinaryParser()

    def _hexdump(self, port: Serial):
        pass

    def run(self):
        print(f"Opening {self.comPort} @ {self.baudRate}")
        try:
            with Serial(self.comPort, self.baudRate, bytesize=self.databit, parity=self.parity, stopbits=self.stopbit, timeout=1, xonxoff=self.xonxoff, rtscts=self.rtscts, dsrdtr=self.dsrdtr) as port:
                self.status.emit(0, None)
                self.running = True
                port.reset_input_buffer()

                while self.running:
                    if port.in_waiting:
                        data = port.read(port.in_waiting)
                        self.rxq.put(data)

                # if self.binary:
                #     while self.running:
                #         if port.in_waiting:
                #             self.rxq.put(port.read(port.in_waiting))                        
                #             # sync = port.read(1)

                #             # if sync in self.parser.syncs:
                #             #     packet = port.read(self.parser.packets[0].size)
                #             #     crc = self.parser.crcs[0](packet[:-1])
                #             #     print(crc, "hex")
                #             #     print(hex2str(sync) + " " + hex2str(packet))
                # else:
                #     while self.running:
                #         if port.in_waiting:
                #             line = port.read(port.in_waiting)
                #             # line = port.readline()
                #             line = line.decode("ASCII", "replace")
                #             self.rxq.put(line)
                #             # print(line)
                #             # print(hexdump(line))
        except SerialException as err:
            self.status.emit(1, err)
            print(f"Unable to open port: {err}")

    def packetReceived(self):
        return