#!/usr/bin/env python3
"""
    This is a good foundation to build your robot code on
"""

import wpilib
import wpilib.drive
import wpilib.buttons

from networktables import NetworkTables

import navx
from navx import AHRS

class MyRobot(wpilib.TimedRobot):

    #    PID stuff

    def robotInit(self):
        """
        This function is called upon program startup and
        should be used for any initialization code.
        """

        self.timer = wpilib.Timer()

        self.i2c = wpilib.I2C(wpilib.I2C.Port.kOnboard, 4)    

        self.timer.start() 

        pass

    def disabledPeriodic(self):
        self.test = True

        # if self.timer.hasPeriodPassed(2):
        print('address a device')
        res = None
        try:
            res = self.i2c.readOnly(5)
        except Exception as e:
            print('did not receive!')
            print(e)
        print('received bytes:')
        print(res)

    def autonomousInit(self):
        """This function is run once each time the robot enters autonomous mode."""
        self.timer.reset()
        self.timer.start()

    def autonomousPeriodic(self):
        """This function is called periodically during autonomous."""

        pass

    def teleopPeriodic(self):
        pass

if __name__ == "__main__":
    wpilib.run(MyRobot)
    # def push(self):
