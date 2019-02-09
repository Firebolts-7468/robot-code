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

    def robotInit(self):
        """
        This function is called upon program startup and
        should be used for any initialization code.
        """
        self.leftf_motor = wpilib.VictorSP(0)
        self.leftr_motor  = wpilib.VictorSP(1)
        self.rightf_motor = wpilib.VictorSP(2)
        self.rightr_motor = wpilib.VictorSP(3)

        #self.drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)
        self.drive = wpilib.drive.MecanumDrive(self.leftf_motor, self.leftr_motor, self.rightf_motor, self.rightr_motor)
        #(frontLeftMotor, rearLeftMotor, frontRightMotor, rearRightMotor)[source]
        self.stick = wpilib.Joystick(0)
        #Button number 1 is the trigger - Angel and Sam, 1.15.2019
        self.trigger = wpilib.buttons.JoystickButton(self.stick, 1)
        self.button2 = wpilib.buttons.JoystickButton(self.stick, 2)

        # button for rotating to the next cardinal angle (0, 90, 180...)
        self.button3 = wpilib.buttons.JoystickButton(self.stick, 3)

        #buttons for toggling rotation and translation 
        self.button11 = wpilib.buttons.JoystickButton(self.stick, 11)
        self.button12 = wpilib.buttons.JoystickButton(self.stick, 12)

        self.timer = wpilib.Timer()
        # self.light = wpilib.DigitalOutput(0) 
        # self.light2 = wpilib.DigitalOutput(9) 
        # self.shooter1= wpilib.DoubleSolenoid(0,5,4)
        # self.shooter2 = wpilib.DoubleSolenoid(1,2,3)
        self.FirePiston = wpilib.Solenoid(0, 0)
        self.FirePiston2 = wpilib.Solenoid(0, 1)


        wpilib.CameraServer.launch()

        # for the rotate to angle function 
        self.rotateLeft = False

        NetworkTables.initialize(server='10.74.68.2')

        self.navx = navx.AHRS.create_spi()

        # self.light.free()       

        # self.drive.arcadeDrive(-0.5, -0.5)  # Drive forwards at half speed

        # timer variables

        self.timer_running = False
        self.start_time = 0

        self.timer.start()
        self.showMsg = True


        # #PID stuff
        # kP = 0.03
        # kI = 0.00
        # kD = 0.00
        # kF = 0.00


        # kToleranceDegrees = 2.0

        # self.ahrs = AHRS.create_spi()
        # self.ahrs = AHRS.create_i2c()

        # turnController = wpilib.PIDController(
        #     0.03, 0.00, 0.00, 0.00, self.ahrs, output=self
        # )
        # turnController.setInputRange(-180.0, 180.0)
        # turnController.setOutputRange(-1.0, 1.0)
        # turnController.setAbsoluteTolerance(2.0)
        # turnController.setContinuous(True)

        # self.turnController = turnController
        # self.rotateToAngleRate = 0

    def disabledPeriodic(self):
        self.test = True

        # print('we are disabled right now')
        # print(self.navx.getAngle()) 

        # try:
        #     if self.timer.hasPeriodPassed(0.5):
        #         self.sd.putBoolean(
        #             "SupportsDisplacement", self.navx._isDisplacementSupported()
        #         )
        #         self.sd.putBoolean("IsCalibrating", self.navx.isCalibrating())
        #         self.sd.putBoolean("IsConnected", self.navx.isConnected())
        #         self.sd.putNumber("Angle", self.navx.getAngle())
        #         self.sd.putNumber("Pitch", self.navx.getPitch())
        #         self.sd.putNumber("Yaw", self.navx.getYaw())
        #         self.sd.putNumber("Roll", self.navx.getRoll())
        #         self.sd.putNumber("Analog", self.analog.getVoltage())
        #         self.sd.putNumber("Timestamp", self.navx.getLastSensorTimestamp())




        #     wpilib.Timer.delay(0.010)
        # except:
        #     print('it didnt work')

    def autonomousInit(self):
        """This function is run once each time the robot enters autonomous mode."""
        self.timer.reset()
        self.timer.start()

    def autonomousPeriodic(self):
        """This function is called periodically during autonomous."""

        
        #Drive for two seconds
        #if self.timer.get() < 2.0:
             #self.drive.arcadeDrive(-0.5, 0)  # Drive forwards at half speed
        #else:
             #self.drive.arcadeDrive(0, 0)  # Stop robot

    def teleopPeriodic(self):
        """This function is called periodically during operator control."""
        # print('Joysticks twist angle =', self.stick.getTwist())

        # if you hold down buttons 11 or 12, then you can disable rotation or translation.
        if self.button3.get() is False: # only if rotate mode isnt enabled
            if self.button11.get() is True: #only translate
                self.drive.driveCartesian(-.5*self.stick.getX(), .5*self.stick.getY(), 0)
            elif self.button12.get() is True: #only rotate
                self.drive.driveCartesian(0, 0,  -.5*self.stick.getTwist())
            else: #do everything! 
                self.drive.driveCartesian(-.5*self.stick.getX(), .5*self.stick.getY(), -.5*self.stick.getTwist())


        # rotate to the nearest 180 degree mark
        currentAngle = self.navx.getAngle()
        if self.button3.get() is True:
            anglediff = currentAngle % 180 # rotate to nearest 90
            print(anglediff)
            if anglediff >= 5 and anglediff<=-5:
                self.drive.driveCartesian(0,0, .5)





        # if currentAngle > 0 and currentAngle < 90:
        #     targetAngle = 0
        # elif currentAngle > 90 and currentAngle < 180:
        #     targetAngle = 90
        # elif currentAngle > 180 and currentAngle < 270:
        #     targetAngle = 180
        # else:
        #     targetAngle = 270


        # if self.button3.get() is True:
        #     self.rotateLeft = True

        # if self.rotateLeft is True:
        #     self.drive.driveCartesian(0,0, .5)
        #     print(currentAngle)
        #     if targetAngle < self.navx.getAngle() - 5 and targetAngle > self.navx.getAngle() + 5:
        #         self.rotateLeft = False






        triggeron = self.trigger.get()
        buttonon2 = self.button2.get()

        




        # rotateToAngle = False
        # if self.stick.getRawButton(1):
        #     self.ahrs.reset()

        # if self.stick.getRawButton(2):
        #     self.turnController.setSetpoint(0.0)
        #     print('button2')
        #     rotateToAngle = True
        # elif self.stick.getRawButton(3):
        #     self.turnController.setSetpoint(90.0)
        #     rotateToAngle = True
        # elif self.stick.getRawButton(4):
        #     self.turnController.setSetpoint(179.9)
        #     rotateToAngle = True
        # elif self.stick.getRawButton(5):
        #     self.turnController.setSetpoint(-90.0)
        #     rotateToAngle = True

        # if rotateToAngle:
        #     self.turnController.enable()
        #     currentRotationRate = self.rotateToAngleRate
        # else:
        #     self.turnController.disable()
        #     currentRotationRate = self.stick.getTwist()


        # yaw0 = self.navx.getAngle()

        # buttonon3= self.button3.get()

        # 
        # print('yaw angle = ', self.navx.getAngle())


        # if abs(self.stick.getTwist()) < 2:
        #     if self.navx.getAngle()-yaw0 > 5:
        #         self.drive.driveCartesian(0,0,-.05)





        
        if self.showMsg:
            print('it works!!!!!!')
            self.showMsg = False

        if triggeron is True:
            # print("firepiston True")
            self.FirePiston.set(True)

        if triggeron is False:
            # print("firepiston False")
            self.FirePiston.set(False)

        if buttonon2 is True:
            # print("firepiston2 True")
            self.FirePiston2.set(True)

        if buttonon2 is False:
            # print("firepiston2 False")
            self.FirePiston2.set(False)
            

            
    def push(self):
        self.shooter1.set(wpilib.DoubleSolenoid.Value.kForward)
        self.shooter2.set(wpilib.DoubleSolenoid.Value.kForward)

    def pull(self):
        self.shooter1.set(wpilib.DoubleSolenoid.Value.kReverse)
        self.shooter2.set(wpilib.DoubleSolenoid.Value.kReverse)
   
    def turnoff(self):
        self.shooter1.set(wpilib.DoubleSolenoid.Value.kOff)
        self.shooter2.set(wpilib.DoubleSolenoid.Value.kOff)


    def pidWrite(self, output):
        """This function is invoked periodically by the PID Controller,
        based upon navX MXP yaw angle input and PID Coefficients.
        """
        self.rotateToAngleRate = output

if __name__ == "__main__":
    wpilib.run(MyRobot)
    # def push(self):
