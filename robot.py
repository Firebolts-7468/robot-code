#!/usr/bin/env python3
"""
    This is a good foundation to build your robot code on
"""

import wpilib
import wpilib.drive

from networktables import NetworkTables
import wpilib.interfaces as wi



class MyRobot(wpilib.TimedRobot):
    def robotInit(self):
        """
        This function is called upon program startup and
        should be used for any initialization code.
        """
        NetworkTables.initialize()
        self.sd = NetworkTables.getTable("SmartDashboard")
        self.lime = NetworkTables.getTable("limelight")


        self.shooterSpeed = 0





        self.leftMotors = wpilib.Talon(0)
        #self.rearLeft = wpilib.Talon(3)
        
        #self.left = wpilib.SpeedControllerGroup(self.frontLeft, self.rearLeft)

        self.rightMotors = wpilib.Talon(1)
        #self.rearRight = wpilib.Talon(1)
        #self.right = wpilib.SpeedControllerGroup(self.frontRight, self.rearRight)

        self.drive = wpilib.drive.DifferentialDrive(self.leftMotors, self.rightMotors)

        
        self.shooterMotor = wpilib.Talon(4)
        
        self.indexerMotor = wpilib.Talon(5)

        self.intakeMotor = wpilib.Talon(6)
        #self.shooterMotor1.setInverted(True)
        self.intakeOn = False
        self.prevValue = False
       

        self.cycleCount = 0


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
        self.cycleCount+=1


        #first, let's get some inofrmation from our control station, we default to not moving
        xScale = self.sd.getNumber("xScale",0)
        yScale = self.sd.getNumber("yScale",0)
        spinScale = self.sd.getNumber("spinScale",0)
        steeringTrim = self.sd.getNumber("steeringTrim",-0.005)
        
        intakeSpeed = self.sd.getNumber("intakeSpeed",0)
        indexerSpeed = self.sd.getNumber("indexerSpeed",0)
        shooterSpeed = self.sd.getNumber("shooterSpeed",0)

        intakeState = self.sd.getNumber("intakeState","off")
        indexerState = self.sd.getNumber("indexerState","off")
        shooterState = self.sd.getNumber("shooterState","off")

        

        visionP = self.sd.getNumber("visionP",0)


        #here we get the current aiming of the vision system 
        limeTx = self.lime.getNumber("tx",0)
        limeTy = self.lime.getNumber("ty",0)

        if self.cycleCount%200==0:
            print(str(xScale)+' '+str(yScale)+' '+str(shooterSpeed))


        #get values from joystick
        yvalue =  -self.joystick.getY(wi.GenericHID.Hand.kLeftHand)
        xvalue =  self.joystick.getX(wi.GenericHID.Hand.kRightHand)
        leftTrigger = self.joystick.getTriggerAxis(wi.GenericHID.Hand.kLeftHand)
        rightTrigger = self.joystick.getTriggerAxis(wi.GenericHID.Hand.kRightHand)
        
    
        

        if leftTrigger > .1 or rightTrigger >.1:
            self.drive.curvatureDrive(yvalue/yScale, (-leftTrigger+rightTrigger)*spinScale+steeringTrim, True)
        elif self.joystick.getAButton():
            if limeTx>5: limeTx=5
            if limeTx<-5: limeTx=-5
            self.drive.curvatureDrive(0, limeTx*visionP, True)
        else:
            self.drive.curvatureDrive(yvalue/yScale, xvalue/xScale+steeringTrim, False)
        


        if intakeState == "on": 
            self.intakeMotor.set(intakeSpeed)
        else:
            self.intakeMotor.set(0)

        if indexerState == "on": 
            self.indexerMotor.set(indexerSpeed)
        else:
            self.indexerMotor.set(0)

        if shooterState == "on": 
            self.shooterMotor.set(shooterSpeed)
        else:
            self.shooterMotor.set(0)


        #self.drive.arcadeDrive(yvalue/joystickYScale, xvalue/joystickXScale, squareInputs=True)

        #print(yvalue/joystickYScale)
        
        #now, let's send info our driver control station 




        #Here, let's deal with the shooter


        



        # triggervalue = self.joystick.getTriggerAxis(1)
        # if triggervalue > 0.3:
        #     self.shooterMotor.set(shooterSpeed)
        # else:
        #     self.shooterMotor.set(0)
            
        #print("self.shooterSpeed")
        #print(shooterSpeed)
        



        #self.sd.putNumber("joystickXScale",joystickXScale)
        #self.sd.putNumber("joystickYScale",joystickYScale)
        #self.sd.putNumber("shooterSpeed",shooterSpeed)

        #here, let's deal with the indexer

        # btvalue = self.joystick.getAButton()
        # if btvalue == True:
        #     self.indexerMotor.set(0.3)
        # else:
        #     self.indexerMotor.set(0)


            # set up left and right bumpers; leftbumper= negative rightbumper= positve 

        # if self.joystick.getBumper(0) == True:


        #     print(self.shooterSpeed)
        #     if self.leftbusyBump == False:

                
        #         self.shooterSpeed = self.shooterSpeed - 1
        #         self.leftbusyBump = True

        # else:
        #     self.leftbusyBump = False

        # if self.joystick.getBumper(1) == True:


        #     print(self.shooterSpeed)
        #     if self.rightbusyBump == False:


        #         self.shooterSpeed = self.shooterSpeed + 1
        #         self.rightbusyBump = True

        # else:
        #     self.rightbusyBump = False





        
        # btvalue = self.joystick.getBButton()
        
        # if btvalue == True and self.prevValue == False:
        #     self.intakeOn = not self.intakeOn

        # self.prevValue = btvalue




        
  
       



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









