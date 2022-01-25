import struct

import crcmod
import yaml as yml


class BinaryParser:

    FORMAT = {"pad": "x",
          "char": "c",
          "string": "s",
          "int8": "b",
          "uint8": "B",
          "int16": "h",
          "uint16": "H",
          "int32": "i",
          "uint32": "I",
          "int64": "q",
          "uint64": "Q",
          "float": "f",
          "double": "d"}
    
    def __init__(self) -> None:
        self.packets = []
        self.syncs = []
        self.crcs = []
        
        self._definePackets()

    def _definePackets(self) -> None:

        with open("packet.yaml", 'r') as file:
            packets = yml.safe_load(file)
            for key, packet in packets.items():
                structCfg = ""

                if packet["endianness"].lower() == "little":
                    structCfg += "<"
                elif packet["endianness"].lower() == "big":
                    structCfg += ">"
                else:
                    structCfg += "="

                for key, val in packet["Payload"].items():
                    if isinstance(val, dict):
                        structCfg += f"{val['Num']}{self.FORMAT[val['Type']]}"
                    else:
                        structCfg += self.FORMAT[val]

                structCfg += "B"

            self.syncs.append(bytearray.fromhex(packet["Header"]["Sync"]))

            print(self.syncs[0])

            self.packets.append(struct.Struct(structCfg))
            # self.crcs.append(crcmod.predefined.mkCrcFun(packet["CRC"]["Type"]))
            self.crcs.append(crcmod.mkCrcFun(0x1d5, initCrc=0, xorOut=0x00, rev=False))
