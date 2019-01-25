#!/usr/bin/env python3
"""
    This is a good foundation to build your robot code on
"""

import wpilib
import wpilib.drive
import wpilib.buttons

class MyRobot(wpilib.TimedRobot):

    def robotInit(self):
        """
        This function is called upon program startup and
        should be used for any initialization code.
        """
        self.left_motor = wpilib.VictorSP(0)
        self.right_motor = wpilib.VictorSP(1)

        self.drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)
        self.stick = wpilib.Joystick(0)
        #Button number 1 is the trigger - Angel and Sam, 1.15.2019
        self.trigger = wpilib.buttons.JoystickButton(self.stick, 1) 
        self.button2 = wpilib.buttons.JoystickButton(self.stick, 2) 
        self.button3 = wpilib.buttons.JoystickButton(self.stick, 3) 
        self.timer = wpilib.Timer()
        self.light = wpilib.DigitalOutput(0) 
        self.light2 = wpilib.DigitalOutput(9) 
        self.shooter1= wpilib.DoubleSolenoid(0,2,4)
        self.shooter2 = wpilib.DoubleSolenoid(0,3,7)

        wpilib.CameraServer.launch()

        # self.light.free()       

        # self.drive.arcadeDrive(-0.5, -0.5)  # Drive forwards at half speed

        # timer variables

        self.timer_running = False
        self.start_time = 0

        self.timer.start()

    def autonomousInit(self):
        """This function is run once each time the robot enters autonomous mode."""
        self.timer.reset()
        self.timer.start()

    def autonomousPeriodic(self):
        """This function is called periodically during autonomous."""

        
        # Drive for two seconds
        # if self.timer.get() < 2.0:
        #     self.drive.arcadeDrive(-0.5, 0)  # Drive forwards at half speed
        # else:
        #     self.drive.arcadeDrive(0, 0)  # Stop robot

    def teleopPeriodic(self):
        """This function is called periodically during operator control."""
        self.drive.arcadeDrive(self.stick.getY(), -self.stick.getX())
        triggeron = self.trigger.get()
        buttonon2 = self.button2.get()
        buttonon3= self.button3.get()
        

        if buttonon3 is True:
            if not self.timer_running:
                self.start_time = self.timer.get()
                self.timer_running = True

            # if timer is still running

        if self.timer_running:
            self.drive.arcadeDrive(0, 0.7)
            if self.timer.get() - self.start_time > 2:
                self.drive.arcadeDrive(0, 0)
                self.timer_running = False

        if buttonon2 is True:
            self.light2.set(0)
        if buttonon2 is False:
            self.light2.set(1)   

        if triggeron is True:
            self.light.set(0)

        if triggeron is False:
            self.light.set(1)
            
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
