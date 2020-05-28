#!/usr/bin/python

from enum import Enum


# fake wrapper class for the libsigrokdecode

class Decoder:
    OUTPUT_ANN = "OUTPUT_ANN"
    OUTPUT_PYTHON = "OUTPUT_PYTHON"
    OUTPUT_BINARY = "OUTPUT_BINARY"
    OUTPUT_META = "OUTPUT_META"

    def register(self, output_type):
        self.output_type = output_type
        if (output_type == self.OUTPUT_ANN):
            return 0
        elif (output_type == self.OUTPUT_PYTHON):
            return 1
        elif (output_type == self.OUTPUT_BINARY):
            return 2
        elif (output_type == self.OUTPUT_META):
            return 3
        pass

    def start(self):
        self.packets = []

    def reset(self):
        self.packets = []

    def metadata(self, key, value):
        pass

    def put(self, ss, es, output_type, data):
        self.packets.append({
            "output_type": output_type,
            "ss": ss,
            "es": es,
            "data": data
        })

    def processLogicDataSPI(self, logicData):
        sigrokData = [
            "DATA",  # TODO figure out that Logic has types other than "result"
            logicData.data.mosi,
            logicData.data.miso,
        ]
        self.decode(logicData["start_time"], logicData["end_time"], sigrokData)

    def processLogicDataI2C(self, logicData):
        '''
        OUTPUT_PYTHON format:

        Packet:
        [<ptype>, <pdata>]

        <ptype>:
         - 'START' (START condition)
         - 'START REPEAT' (Repeated START condition)
         - 'ADDRESS READ' (Slave address, ['Read', 'Rd', 'R'])
         - 'ADDRESS WRITE' (Slave address, ['Write', 'Wr', 'W'])
         - 'DATA READ' (Data, read)
         - 'DATA WRITE' (Data, write)
         - 'STOP' (STOP condition)
         - 'ACK' (ACK bit)
         - 'NACK' (NACK bit)
         - 'BITS' (<pdata>: list of data/address bits and their ss/es numbers)

        <pdata> is the data or address byte associated with the 'ADDRESS*' and 'DATA*'
        command. Slave addresses do not include bit 0 (the READ/WRITE indication bit).
        For example, a slave address field could be 0x51 (instead of 0xa2).
        For 'START', 'START REPEAT', 'STOP', 'ACK', and 'NACK' <pdata> is None.

        For address or data the order is:

        Store individual bits and their start/end samplenumbers.
        In the list, index 0 represents the LSB (I²C transmits MSB-first).
        We have the bit times ss/es of the Logicdata
        self.putp(['BITS', self.bits]) bits are present here individually with ss/es

        self.putp([cmd, d]) cmd is the ptype string ("ADDRESS/DATA READ/WRITE")

        self.putb([bin_class, bytes([d])])

        for bit in self.bits:
            self.put(bit[1], bit[2], self.out_ann, [5, ['%d' % bit[0]]])


        '''
        print(logicData)
        if (logicData["type"] == "start"):
            self.decode(logicData["start_time"], logicData["end_time"], ["START", None])
        elif (logicData["type"] == "stop"):
            self.decode(logicData["start_time"], logicData["end_time"], ["STOP", None])
        elif (logicData["type"] == "ack"):
            self.decode(logicData["start_time"], logicData["end_time"], ["ACK", None])
        elif (logicData["type"] == "nack"):
            self.decode(logicData["start_time"], logicData["end_time"], ["NACK", None])
        elif (logicData["type"] == "address"):
            sigrokType = "ADDRESS WRITE"
            if (int.from_bytes(logicData["data"]["address"], byteorder='big') & 0b1):
                sigrokType = "ADDRESS READ"
            self.decode(logicData["start_time"], logicData["end_time"], [sigrokType, logicData["data"]["address"]])
            return
        elif (logicData["type"] == "data"):
            sigrokType = "DATA WRITE"
            if (int.from_bytes(logicData["data"]["data"], byteorder='big') & 0b1) :
                sigrokType = "DATA READ"
            self.decode(logicData["start_time"], logicData["end_time"], [sigrokType, logicData["data"]["data"]])
            self.decode(logicData["start_time"], logicData["end_time"], ["BITS", logicData["data"]["data"]])
            return
        return

    def processLogicDataUART(self, logicData):
        sigrokData = []
        if (logicData["data"]["parity_error"]):
            sigrokData = ["PARITY ERROR", 0, logicData["data"]["value"]]
        elif (logicData.data.framing_error):
            sigrokData = ["INVALID STOPBIT", 0, logicData["data"]["value"]]
        else:
            uartValue = logicData.data.value
            if (logicData["data"].address):
                uartValue = uartValue + 256
            sigrokData = ["DATA", 0, uartValue]  # single channel only -> always RX data

        self.decode(logicData["start_time"], logicData["end_time"], sigrokData)

    def generate_logic_result(self):
        if (len(self.packets) == 0):
            return

        ret = []
        for packet in self.packets:
            typeString = ""
            if (packet.type == self.OUTPUT_ANN):
                ret.append({
                    "type": self.annotations[packet.data[0]],
                    "start_time": packet.ss,
                    "end_time": packet.es,
                    "data": {
                        "data": packet.data[1],
                    }
                })
        self.packets = []
        if (len(ret) == 1):
            return ret[0]
        return ret
