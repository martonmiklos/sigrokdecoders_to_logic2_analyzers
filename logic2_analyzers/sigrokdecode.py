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
        sigrokData = []
        if (logicData["type"] == "start"):
            sigrokData = ["START", None]
        elif (logicData["type"] == "stop"):
            sigrokData = ["STOP", None]
        elif (logicData["type"] == "address"):
            sigrokData = ["ADDRESS READ", logicData["data"]["address"]]
        elif (logicData["type"] == "data"):
            sigrokData = ["DATA READ", logicData["data"]["data"]]
        else:
            return
        self.decode(logicData["start_time"], logicData["end_time"], sigrokData)

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
