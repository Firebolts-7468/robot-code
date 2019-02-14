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


    target = ntproperty("/camera/target", (0, 0.0, 0.0)) #found, angle and distance
    

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
        self.leftf_motor = wpilib.VictorSP(0)
        self.leftr_motor  = wpilib.VictorSP(1)
        self.rightf_motor = wpilib.VictorSP(2)
        self.rightr_motor = wpilib.VictorSP(3)

        # Then we set up our climbing motor
        #self.climb_motor = wpilib.VictorSP(4)


        # Next, let's define the angles for the targets angles are positive clockwise looking from above
        self.target_angles = {
            'starting': 0,
            'panel_pickup':180,
            'front_cargo':0,
            'left_side_cargo':90,
            'right_side_cargo':270,
            'right_front_rocket': 29,
            'right_rear_rocket': 151,
            'left_front_rocket': 331,
            'left_rear_rocket': 209,
            }

        #Set up to drive with mecanum wheels
        self.drive = wpilib.drive.MecanumDrive(self.leftf_motor, self.leftr_motor, self.rightf_motor, self.rightr_motor)
        #set up the joystick
        self.joystick = wpilib.Joystick(0)
        #set the ID of the one pneumatic control module (PCM) we are going to use
        self.pneumatic_control_ID = 0

        # Now, let's set up all of the buttons we are going to use

        #Trigger will shoot the panel eject solenoids
        self.trigger_button = wpilib.buttons.JoystickButton(self.joystick, 1)
        #thumb button will retract the panel eject solenoids
        self.thumb_button = wpilib.buttons.JoystickButton(self.joystick, 2)
        # button3 for controlling the robot to a preset target angle (see self.target_angles above) 
        self.snap_angle_button = wpilib.buttons.JoystickButton(self.joystick, 3)
        # button4 for controlling the robot to be lined up with the target in crosstrack
        self.control_crosstrack_button = wpilib.buttons.JoystickButton(self.joystick, 4)
        #button 7 sets zero point for angle
        self.zero_button = wpilib.buttons.JoystickButton(self.joystick, 7)
        #button 5 is to only translate 
        self.translate_only_button = wpilib.buttons.JoystickButton(self.joystick, 5)
        #button 6 is to only rotate
        self.rotate_only_button = wpilib.buttons.JoystickButton(self.joystick, 6)

        #if we want to use the throttle we should set it up here
        self.useThrottle = True
        #timer so that we can retract the solenoid some time after we let go of the button
        self.trigger_timer = wpilib.Timer()
        self.trigger_timer.start()
        self.solenoid_delay = 0.5 #seconds
 

      
        

        #If we want to set up digital output like LEDs, we can do it here
            # self.light = wpilib.DigitalOutput(0) 
            # self.light2 = wpilib.DigitalOutput(9) 

        # Now, let's set up the solenoids we are going to use    
        self.panel_eject_solenoid = wpilib.Solenoid(self.pneumatic_control_ID, 0)
        self.panel_retract_solenoid = wpilib.Solenoid(self.pneumatic_control_ID, 1)
        self.panel_new_solenoid = wpilib.Solenoid(self.pneumatic_control_ID, 2)


        #self.climb_lift_solenoid = wpilib.Solenoid(self.pneumatic_control_ID, 2)

        #launch the camera server so that we can view the USB camera on the driver station
        #wpilib.CameraServer.launch()
        #now, make an object for the vision camera
        self.visionCamera = VisionCamera()

        #Next, let's set up all the stuff to do with the IMU
        self.ahrs = AHRS.create_spi()

        #We should define some variables for snapping to the closest target angle
        self.snappingToAngle = False
        self.controllingCrosstrack = False

        # Define all the variables for controlling rotation
        self.rotation_PID_vars = {
            'kP': 0.0005,
            'kI': 0,
            'kD': 0.02,
            'kF': 0.00,
            'max': 1,
            'kToleranceDegrees' : 2.0,
        }

        self.lastRotation = 0
        #first, we need to instantiate our objects up above
        self.rotation_source = Rotation_Source(self.ahrs)
        self.rotation_output = PID_Output()
        #then, we make the PID object
        self.rotation_PID = wpilib.PIDController(
            self.rotation_PID_vars['kP'], 
            self.rotation_PID_vars['kI'], 
            self.rotation_PID_vars['kD'], 
            self.rotation_PID_vars['kF'], 
            self.rotation_source, 
            self.rotation_output, 
            
        )
        #then, we set some parameters
        self.rotation_PID.setInputRange(0, 360)
        self.rotation_PID.setContinuous(True)
        self.rotation_PID.setOutputRange(-self.rotation_PID_vars['max'], self.rotation_PID_vars['max'])
        self.rotation_PID.setAbsoluteTolerance(self.rotation_PID_vars['kToleranceDegrees'])



        # Define all the variables for controlling crosstrack
        self.crosstrack_PID_vars = {
            'kP': 0.03,
            'kI': 0.0,
            'kD': 0.00,
            'kF': 0.00,
            'max': .2,
            'kTolerance' : 2.0,
        }

        #first, we need to instantiate our objects up above
        self.crosstrack_output = PID_Output()
        #then, we make the PID object
        self.crosstrack_PID = wpilib.PIDController(
            self.crosstrack_PID_vars['kP'], 
            self.crosstrack_PID_vars['kI'], 
            self.crosstrack_PID_vars['kD'], 
            self.crosstrack_PID_vars['kF'], 
            self.visionCamera, 
            self.crosstrack_output
        )
        #then, we set some parameters
        self.crosstrack_PID.setInputRange(-100, 100)
        self.crosstrack_PID.setOutputRange(-self.crosstrack_PID_vars['max'], self.crosstrack_PID_vars['max'])
        self.crosstrack_PID.setAbsoluteTolerance(self.crosstrack_PID_vars['kTolerance'])
        
        #initiate the "zero out" function
        self.zeroOnce = 0
   
    def disabledPeriodic(self):
        #this looks for data from the camera
        self.loopCounter += 1

        #if self.loopCounter%10==0:
        #    print("Heading is: "+str(self.rotation_source.pidGet()))





    def autonomousInit(self):
        """This function is run once each time the robot enters autonomous mode."""
        #self.timer.reset()
        #self.timer.start()

    def autonomousPeriodic(self):
        """This function is called periodically during autonomous."""


    def teleopPeriodic(self):
        """This function is called periodically during operator control."""
        self.loopCounter += 1
        #first, let's get all the data from the joystick so we know what we are working with
        stick = {
            'x': -self.joystick.getX(),
            'y': self.joystick.getY(),
            'rot': -.8*self.joystick.getTwist(),
            'throttle': (-self.joystick.getThrottle()+1)/2,
            'trigger_button': self.trigger_button.get(),
            'thumb_button': self.thumb_button.get(),
            'zero_button' : self.zero_button.get(),
            'snap_angle_button': self.snap_angle_button.get(),
            'translate_only_button': self.translate_only_button.get(),
            'rotate_only_button': self.rotate_only_button.get(),
            'control_crosstrack_button': self.control_crosstrack_button.get(),
        }

        #if self.loopCounter%100==0:
        #    print('P: %s, I: %s, D:%s'%(self.rotation_PID_vars['kP'],self.rotation_PID_vars['kI'],self.rotation_PID_vars['kD']))

        if self.loopCounter%30==0 and self.target[0]>0:
            print('See target at %s'%(self.target[2]))

        #print(self.rotation_PID_vars['kP'])

        if stick['zero_button']:
            if self.zeroOnce == 0:
                print("Old angle offset was: " + str(self.rotation_source.angleOffset))
                self.rotation_source.zeroAngleOffset()
                print("New angle offset is: " + str(self.rotation_source.angleOffset))
                print("Heading is: " + str(self.rotation_source.pidGet()))
                self.zeroOnce = self.zeroOnce + 1

        if stick['zero_button'] is False:
            self.zeroOnce = 0

        #print(stick)

        #if we are going to use the throttle input, we should do that first
        if self.useThrottle:
            stick['x'] = stick['x']*stick['throttle']
            stick['y'] = stick['y']*stick['throttle']
            stick['rot'] = stick['rot']*stick['throttle']


        #so, if we want to translate only, we need to zero out the input for twitsting
        if stick['translate_only_button']:
            stick['rot'] = 0
        #if we want to rotate only, we should zero out the x and y
        if stick['rotate_only_button']:  
            stick['x'] = 0
            stick['y'] = 0
            print("Position: %s"%(self.rotation_source.pidGet()))


        #set the solenoids based on the button
        if stick['trigger_button']:
            #when we press the trigger, open the valve
            self.panel_eject_solenoid.set(True)
            self.trigger_timer.reset()
        else:
            #if the delay has pased, we should turn off the solenoid
            if self.trigger_timer.hasPeriodPassed(self.solenoid_delay):
                self.panel_eject_solenoid.set(False)


        #self.panel_eject_solenoid.set(stick['trigger_button'])
        self.panel_new_solenoid.set(stick['thumb_button'])

       
        #In order to snap to control, we need to find the angle we are currently at, then set the target angle 
            #to the closest target angle
        if stick['snap_angle_button']: 
            if not self.snappingToAngle:
                #this is the first time, so we need to set where to snap to
                angleError = 360 #start with a big error
                currentAngle = self.rotation_source.pidGet() #get the angle the same way the PID control will
                print('Starting angle: %s' %currentAngle)
                #for any angle that has a smaller error, set the setpoint to it
                for name,angle in self.target_angles.items():
                    #angle_difference = 180 - abs(abs(currentAngle - angle) - 180)
                    angle_difference = 180 - abs(abs(currentAngle - angle) - 180)
                    if angle_difference < angleError:
                        print('Setting angle to %s for %s with diff: %s' % (name,angle,angle_difference))
                        angleError = angle_difference
                        self.rotation_PID.setSetpoint((angle+180)%360)
                        #self.rotation_PID.setSetpoint(angle)
                self.rotation_PID.enable()
                self.snappingToAngle = True
            else:    

                if self.loopCounter%10 ==0:
                    print("Error: %s, Position: %s, Setpoint: %s"%(self.rotation_source.pidGet()-180-self.rotation_PID.getSetpoint(),self.rotation_source.pidGet(),self.rotation_PID.getSetpoint()))

                #doing a little extra here to not let it change too quickly
                maxChange = 0.05
                if abs(self.lastRotation-self.rotation_output.correction)>maxChange:
                    if self.lastRotation < self.rotation_output.correction:
                        stick['rot'] = self.lastRotation+maxChange
                    else:
                        stick['rot'] = self.lastRotation-maxChange
                else:
                    stick['rot'] = self.rotation_output.correction
                self.lastRotation = stick['rot']


        else:
            #if we aren't snapping, we should reset this variable and turn off control
            self.snappingToAngle = False
            self.rotation_PID.disable()
            self.lastRotation = 0




        #for control crosstrack, we need to take the control signal from crosstrack PID
        if stick['control_crosstrack_button']:
            if not self.controllingCrosstrack:
                self.crosstrack_PID.setSetpoint(0)
                self.crosstrack_PID.enable()  
                self.controllingCrosstrack = True  
            else:
                stick['x'] = self.crosstrack_output.correction


        #now that we have figured everything out, we need to a actually drive the robot        
        self.drive.driveCartesian(stick['x'], stick['y'], stick['rot'])

    
if __name__ == "__main__":
    wpilib.run(MyRobot, physics_enabled=True)



# Links for PID
# https://www.chiefdelphi.com/t/python-drivetrain-pid/161488/2
# https://frc-pdr.readthedocs.io/en/latest/control/pid_control.html#tuning-methods
# https://robotpy.readthedocs.io/projects/wpilib/en/latest/_modules/wpilib/interfaces/pidsource.html#PIDSource.getPIDSourceType


#Steps to do with students
  # Show that fused heading changes with robot orientation
  # turn off all joystick entry, and set a target of 30deg off of starting, and control to it









