import wpilib
import struct
from networktables import NetworkTables
from networktables.util import ntproperty





class Rotation_Source(wpilib.interfaces.PIDSource):
    def __init__(self, ahrs, angleOffset = 0):
        self.ahrs = ahrs
        self.angleOffset = angleOffset

    def pidGet(self):
        if self.ahrs.isMagnetometerCalibrated():
            #print('fused %s'%self.ahrs.getFusedHeading())
            return (self.ahrs.getFusedHeading()-self.angleOffset)%360
        else:
            print('not fused')
            return (self.ahrs.getAngle()-self.angleOffset)%360

    def zeroAngleOffset(self):
        if self.ahrs.isMagnetometerCalibrated():
            currentAngle = self.ahrs.getFusedHeading()
            self.angleOffset = currentAngle
        else:
            currentAngle = self.ahrs.getAngle()
            self.angleOffset = currentAngle 

    def getPIDSourceType(self):
        return 'fused heading'
    
    def setPIDSourceType(self, source_type):
        return True



class PID_Output(wpilib.interfaces.PIDOutput):
    def __init__(self):
        self.correction = 0;

    def pidWrite(self, value):
        self.correction = value

   

class VisionCamera(wpilib.interfaces.PIDSource):
    
    target = ntproperty("/camera/target", (0, 0.0, 0.0)) #found, angle and distance

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
        found, offset, distance = self.target
        #print('offset: %s, dist:%s'%( offset, distance))

        return offset
        
    def getPIDSourceType(self):
        return 'crosstrack'
    
    def setPIDSourceType(self, source_type):
        return True