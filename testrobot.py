#!/usr/bin/env python3
"""
    This is a good foundation to build your robot code on
"""

import wpilib
import wpilib.drive

from networktables import NetworkTables
import wpilib.interfaces as wi

import os

print("OS information: %s" % str(os.uname()))

print("OS machine type: %s" % os.uname().machine)


class MyRobot(wpilib.TimedRobot):


    def robotInit(self):

        # #Get information from network tables
        NetworkTables.initialize()
        self.sd = NetworkTables.getTable("SmartDashboard")
        self.lime = NetworkTables.getTable("limelight")



    def disabledPeriodic(self):
        pass

    def autonomousInit(self):
        """This function is run once each time the robot enters autonomous mode."""
        #self.timer.reset()
        #self.timer.start()
        pass

    def autonomousPeriodic(self):
        """This function is called periodically during autonomous."""
        self.teleopPeriodic()


    def teleopPeriodic(self):
        
       pass

      
        


if __name__ == "__main__":
    wpilib.run(MyRobot, physics_enabled=True)




