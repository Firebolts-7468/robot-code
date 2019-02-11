import wpilib
import struct

class VisionCamera(wpilib.interfaces.PIDSource):
    def __init__(self, addr=4):
        self.i2c = wpilib.I2C(wpilib.I2C.Port.kOnboard, addr)

        self.msg_length = 4
        self.data = []


    def poll(self):
        res = []
        try:
            res = self.i2c.readOnly(self.msg_length)
        except Exception as e:
            pass

        try:
            self.data = struct.unpack('<i', bytearray(res))
        except:
            self.data = -9000

        #print('got data: %i' % self.data)

    def pidGet(self):
        if len(self.data)>0:
            return data[0]
        else:
            return 0
        