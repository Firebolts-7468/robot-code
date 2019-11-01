#!/usr/bin/env python3
"""
    This is a good foundation to build your robot code on
"""

import wpilib
import wpilib.drive
import wpilib.buttons

from networktables import NetworkTables
from networktables.util import ntproperty

import navx
from navx import AHRS

from helpers import Rotation_Source, PID_Output, VisionCamera


class MyRobot(wpilib.TimedRobot):

    def robotInit(self):
        """
        This function is called upon program startup and
        should be used for any initialization code.
        """
        self.loopCounter = 0

        # Set up the network tables so we can talk to the driver station
        NetworkTables.initialize(server='10.74.68.2')

        #This gets us the dashboard entry, so that we can put information there
        self.dashboard = NetworkTables.getTable('SmartDashboard')
        #this tests transferring a value from the robot to the driver's station
        self.dashboard.putNumber("Test Number", 5)

        # Set up all of our drive motors
        self.left_front_motor = wpilib.VictorSP(0)
        self.left_rear_motor  = wpilib.VictorSP(1)
        self.right_front_motor = wpilib.VictorSP(2)
        self.right_rear_motor = wpilib.VictorSP(3)

        #Then we set up our climbing motor
        self.climb_motor = wpilib.VictorSP(4)

        #Set up to drive with mecanum wheels
        self.drive = wpilib.drive.MecanumDrive(self.left_front_motor, self.left_rear_motor, self.right_front_motor, self.right_rear_motor)
        #set up the joystick
        self.joystick = wpilib.Joystick(0)
        #set the ID of the one pneumatic control module (PCM) we are going to use
        self.pneumatic_control_ID = 0

        #let's define the digital inputs
        self.climb_stop = wpilib.DigitalInput(0)  #this is the limit switch that trips at the end of the climb


        # Now, let's set up all of the buttons we are going to use

        #Trigger will shoot the panel eject solenoids
        self.trigger_button = wpilib.buttons.JoystickButton(self.joystick, 1)
        #Lifts the panel arm
        self.panel_up_button = wpilib.buttons.JoystickButton(self.joystick, 3)
        #drops the panel arm
        self.panel_down_button = wpilib.buttons.JoystickButton(self.joystick, 5)

        #Drop the foot
        self.foot_release = wpilib.buttons.JoystickButton(self.joystick, 12)
        #Undo the foot release
        self.foot_unrelease = wpilib.buttons.JoystickButton(self.joystick, 11)
        #Pull in the climbing wire to climb
        self.climb_up = wpilib.buttons.JoystickButton(self.joystick, 10)
        #:et out the climbing wire
        self.climb_down = wpilib.buttons.JoystickButton(self.joystick, 9)
        #Lift the robot with the big solenoids
        self.robot_lift = wpilib.buttons.JoystickButton(self.joystick, 8)
        #let the robot back down, although, you need to manually undo the solenoid on the robot
        self.robot_unlift = wpilib.buttons.JoystickButton(self.joystick, 7)


        #timer so that we can retract the solenoid some time after we let go of the button
        self.trigger_timer = wpilib.Timer()
        self.trigger_timer.start()
        self.solenoid_delay = 0.5 #seconds


        # Now, let's set up the solenoids we are going to use
        self.panel_eject_solenoid = wpilib.Solenoid(self.pneumatic_control_ID, 0)
        self.panel_lift_solenoid = wpilib.Solenoid(self.pneumatic_control_ID, 4)
        self.robot_lift_solenoid = wpilib.Solenoid(self.pneumatic_control_ID, 2)
        self.robot_unlift_solenoid = wpilib.Solenoid(self.pneumatic_control_ID, 5)
        self.foot_release_solenoid = wpilib.Solenoid(self.pneumatic_control_ID, 3)
        self.panel_down_solenoid = wpilib.Solenoid(self.pneumatic_control_ID, 1)

        #launch the camera server so that we can view the USB camera on the driver station
        wpilib.CameraServer.launch()


    def disabledPeriodic(self):
        """We can put stuff here we want our robot to do when it is disabled"""
        x = 1


    def autonomousInit(self):
        """This function is run once each time the robot enters autonomous mode."""
        self.vision_timer.start()

    def autonomousPeriodic(self):
        """This function is called periodically during autonomous."""
        #when we are in autonomous mode, we just want to run the same code as we do in teleopPeriodic
        self.teleopPeriodic()

    def teleopPeriodic(self):
        """This function is called periodically during operator control."""
        self.loopCounter += 1
        #first, let's get all the data from the joystick so we know what we are working with
        stick = {
            'x': -self.joystick.getX(),
            'y': self.joystick.getY(),
            'rot': -.5*self.joystick.getTwist(),
            'throttle': (-self.joystick.getThrottle()+1)/2,  #This gives us a throttle from 0 to 1
            'trigger_button': self.trigger_button.get(),
            'robot_lift': self.robot_lift.get(),
            'robot_unlift': self.robot_unlift.get(),
            'climb_up': self.climb_up.get(),
            'climb_down': self.climb_down.get(),
            'panel_up_button': self.panel_up_button.get(),
            'panel_down_button': self.panel_down_button.get(),
            'foot_release': self.foot_release.get(),
            'foot_unrelease': self.foot_unrelease.get(),
        }


        #Use the throttle to scale the inputs from the joystick
        stick['x'] = stick['x']*stick['throttle']  #maybe we should add logic to this line??
        stick['y'] = stick['y']*stick['throttle']
        stick['rot'] = stick['rot']*stick['throttle']

        #If the climb button is pressed, and the limit stop isn't hit we should climb at the throttle speed
        if stick['climb_up'] and self.climb_stop.get()==False:
            self.climb_motor.set(stick['throttle'])
        #else, if the climb down is pressed, climb at negative throttle speed
        elif stick['climb_down']:
            self.climb_motor.set(-stick['throttle'])
        #Else, set the climb motor to zero
        else:
            self.climb_motor.set(0)

        #set the solenoids based on the button
        if stick['trigger_button']:
            #when we press the trigger, open the valve
            self.panel_eject_solenoid.set(True)
            #Then, reset the timer so we know when to release the trigger solenoids
            self.trigger_timer.reset()
        else:
            #if the delay has pased, we should turn off the solenoid
            if self.trigger_timer.hasPeriodPassed(self.solenoid_delay):
                self.panel_eject_solenoid.set(False)


        #Based on the lift buttons, we should activate or deactive the lift solenoids
        if stick['robot_lift']:
            self.robot_lift_solenoid.set(True)
            self.robot_unlift_solenoid.set(False)

        if stick['robot_unlift']:
            self.robot_lift_solenoid.set(False)
            self.robot_unlift_solenoid.set(True)

        if stick['panel_up_button']:
            self.panel_lift_solenoid.set(False)
            self.panel_down_solenoid.set(True)

        if stick['panel_down_button']:
            self.panel_lift_solenoid.set(True)
            self.panel_down_solenoid.set(False)

        if stick['foot_release']:
            self.foot_release_solenoid.set(True)

        if stick['foot_unrelease']:
            self.foot_release_solenoid.set(False)

        #now that we have figured everything out, we need to a actually drive the robot
        self.drive.driveCartesian(stick['x'], stick['y'], stick['rot'])

    #logic to stop the robot from hitting the wall
    def stopthewall(self):
        int frontdist = getDistance()
        int safedist = 4
        if frontdist <= safedist:
            return True
        else:
            return False


if __name__ == "__main__":
    wpilib.run(MyRobot, physics_enabled=True)

#Serena was here










