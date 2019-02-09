import wpilib

class Camera():
    def __init__(self, addr=4):
        self.i2c = wpilib.I2C(wpilib.I2C.Port.kOnboard, addr)

        self.msg_length = 5
        self.data = []

    def poll(self):
        self.data = []
        try:
            self.data = self.i2c.readOnly(self.msg_length)
        except Exception as e:
            pass
        print('got data: %s' % self.data)