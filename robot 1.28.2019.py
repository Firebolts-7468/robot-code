#!/usr/bin/env python3
"""
    This is a good foundation to build your robot code on
"""

import wpilib
import wpilib.drive
import wpilib.buttons

from networktables import NetworkTables

import navx

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
        self.button3 = wpilib.buttons.JoystickButton(self.stick, 3)

        self.timer = wpilib.Timer()
        self.light = wpilib.DigitalOutput(0) 
        self.light2 = wpilib.DigitalOutput(9) 
        self.shooter1= wpilib.DoubleSolenoid(0,5,4)
        self.shooter2 = wpilib.DoubleSolenoid(1,2,3)

        wpilib.CameraServer.launch()

        NetworkTables.initialize(server='10.74.68.2')

        self.navx = navx.AHRS.create_spi()

        # self.light.free()       

        # self.drive.arcadeDrive(-0.5, -0.5)  # Drive forwards at half speed

        # timer variables

        self.timer_running = False
        self.start_time = 0

        self.timer.start()
        self.showMsg = True

    def disabledPeriodic(self):
        self.test = True

        print(self.navx.getAngle())

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

        print('test periodic')

        self.drive.driveCartesian(-.5*self.stick.getX(), .5*self.stick.getY(), -.5*self.stick.getTwist())
        triggeron = self.trigger.get()
        buttonon2 = self.button2.get()
        buttonon3= self.button3.get()
        

        
        if self.showMsg:
            print('it works!!!!!!')
            self.showMsg = False

        if buttonon3 is True:
            if not self.timer_running:
                self.start_time = self.timer.get()
                self.timer_running = True

            # if timer is still running

        if self.timer_running:
            self.drive.driveCartesian(0, 0.7, 0)
            if self.timer.get() - self.start_time > 2:
                self.drive.driveCartesian(0, 0, 0)
                self.timer_running = False

        # if buttonon2 is True:
        #     self.light2.set(0)
        # if buttonon2 is False:
        #     self.light2.set(1)   

        # if triggeron is True:
        #     self.push()
        #     # self.light.set(0)

        # if triggeron is False:
        #     self.pull()
        #     # self.light.set(1)

            

            
    def push(self):
        self.shooter1.set(wpilib.DoubleSolenoid.Value.kForward)
        self.shooter2.set(wpilib.DoubleSolenoid.Value.kForward)

    def pull(self):
        self.shooter1.set(wpilib.DoubleSolenoid.Value.kReverse)
        self.shooter2.set(wpilib.DoubleSolenoid.Value.kReverse)
   
    def turnoff(self):
        self.shooter1.set(wpilib.DoubleSolenoid.Value.kOff)
        self.shooter2.set(wpilib.DoubleSolenoid.Value.kOff)

if __name__ == "__main__":
    wpilib.run(MyRobot)
    # def push(self):
