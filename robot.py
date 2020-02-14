#!/usr/bin/env python3
"""
    This is a good foundation to build your robot code on
"""

import wpilib
import wpilib.drive
import wpilib.buttons

from networktables import NetworkTables


NetworkTables.initialize()
sd = NetworkTables.getTable("SmartDashboard")

class MyRobot(wpilib.TimedRobot):
    def robotInit(self):
        """
        This function is called upon program startup and
        should be used for any initialization code.
        """
        self.shooterSpeed = 0
        self.leftbusyBump = False
        self.rightbusyBump = False
        self.busyTrig = False
        self.frontLeft = wpilib.Talon(0)
        self.rearLeft = wpilib.Talon(1)
        self.left = wpilib.SpeedControllerGroup(self.frontLeft, self.rearLeft)

        self.frontRight = wpilib.Talon(2)
        self.rearRight = wpilib.Talon(3)
        self.right = wpilib.SpeedControllerGroup(self.frontRight, self.rearRight)

        self.drive = wpilib.drive.DifferentialDrive(self.left, self.right)

        
        self.shooterMotor = wpilib.Talon(4)
        
        self.indexerMotor = wpilib.Talon(5)

        self.intakeMotor = wpilib.Talon(6)
        #self.shooterMotor1.setInverted(True)
        self.intakeOn = False
        self.prevValue = False
       


       




        self.joystick = wpilib.XboxController(0)




        

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
        # self.drive.driveCartesian(stick['x'], stick['y'], stick['rot'])
        #speeed for X change to same as Y

        #write a value to a network table that you can see on the driver station 

        #when you push a button, show a value, when you release, show another value



        yvalue =  self.joystick.getY(0) / 3
        xvalue =  self.joystick.getX(0) / 3
        btvalue = self.joystick.getXButton()
        if btvalue == True:
            yvalue = yvalue / 4
            xvalue = xvalue / 4
        self.drive.arcadeDrive(yvalue, xvalue, squareInputs=True)
        
        triggervalue = self.joystick.getTriggerAxis(1)
        if triggervalue > 0.3:
            self.shooterMotor.set(0.5)
        else:
            self.shooterMotor.set(0)
            

        btvalue = self.joystick.getAButton()
        if btvalue == True:
            self.indexerMotor.set(0.3)
        else:
            self.indexerMotor.set(0)


            # set up left and right bumpers; leftbumper= negative rightbumper= positve 

        if self.joystick.getBumper(0) == True:


            print(self.shooterSpeed)
            if self.leftbusyBump == False:

                
                self.shooterSpeed = self.shooterSpeed - 1
                self.leftbusyBump = True

        else:
            self.leftbusyBump = False

        if self.joystick.getBumper(1) == True:


            print(self.shooterSpeed)
            if self.rightbusyBump == False:


                self.shooterSpeed = self.shooterSpeed + 1
                self.rightbusyBump = True

        else:
            self.rightbusyBump = False





        
        btvalue = self.joystick.getBButton()
        
        if btvalue == True and self.prevValue == False:
            self.intakeOn = not self.intakeOn

        self.prevValue = btvalue




        if self.intakeOn == True:
            self.intakeMotor.set(0.5)
        else:
            self.intakeMotor.set(0)



        # # how to hook up a button to a motor
        # aValue = self.joystick.getSomeButton()

        # # if it's a normal button
        # if aValue == True:
        #     self.theMotor.set(speedValue)
     
        # # if it's an axis (like a joystick or a trigger)
        # if aValue > someLimit:
        #     self.theMotor.set(speedValue)


        


if __name__ == "__main__":
    wpilib.run(MyRobot, physics_enabled=True)



# Links for PID
# https://www.chiefdelphi.com/t/python-drivetrain-pid/161488/2
# https://frc-pdr.readthedocs.io/en/latest/control/pid_control.html#tuning-methods
# https://robotpy.readthedocs.io/projects/wpilib/en/latest/_modules/wpilib/interfaces/pidsource.html#PIDSource.getPIDSourceType


#Steps to do with students
  # Show that fused heading changes with robot orientation
  # turn off all joystick entry, and set a target of 30deg off of starting, and control to it









