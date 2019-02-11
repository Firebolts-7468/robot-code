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

from visionCamera import VisionCamera


class Rotation_Source(wpilib.interfaces.PIDSource):
    def __init__(self, ahrs, angleOffset = 0):
        self.ahrs = ahrs
        self.angleOffset = angleOffset

    def pidGet(self):
        if self.ahrs.isMagnetometerCalibrated():
            return (self.ahrs.getFusedHeading()-self.angleOffset)%360
        else:
            print('navX is not calibrated')
            return 0

    def getPIDSourceType(self):
        return 'fused heading'
    
    def setPIDSourceType(self, source_type):
        return True



class PID_Output(wpilib.interfaces.PIDOutput):
    def __init__(self):
        self.correction = 0;

    def pidWrite(self, value):
        self.correction = value

   

class MyRobot(wpilib.TimedRobot):


    def robotInit(self):
        """
        This function is called upon program startup and
        should be used for any initialization code.
        """ 

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
        #button 11 is to only translate 
        self.translate_only_button = wpilib.buttons.JoystickButton(self.joystick, 5)
        #button 12 is to only rotate
        self.rotate_only_button = wpilib.buttons.JoystickButton(self.joystick, 6)

        #if we want to use the throttle we should set it up here
        self.useThrottle = False
        self.throttleMax = 1


        #starting the timer, but I don't know why
        #self.timer = wpilib.Timer()

        #If we want to set up digital output like LEDs, we can do it here
            # self.light = wpilib.DigitalOutput(0) 
            # self.light2 = wpilib.DigitalOutput(9) 

        # Now, let's set up the solenoids we are going to use    
        self.panel_eject_solenoid = wpilib.Solenoid(self.pneumatic_control_ID, 0)
        self.panel_retract_solenoid = wpilib.Solenoid(self.pneumatic_control_ID, 1)
        #self.climb_lift_solenoid = wpilib.Solenoid(self.pneumatic_control_ID, 2)

        #launch the camera server so that we can view the USB camera on the driver station
        wpilib.CameraServer.launch()
        #now, make an object for the vision camera
        self.visionCamera = VisionCamera()

        #Next, let's set up all the stuff to do with the IMU
        self.ahrs = AHRS.create_spi()

        #We should define some variables for snapping to the closest target angle
        self.snappingToAngle = False

        # Define all the variables for controlling rotation
        self.rotation_PID_vars = {
            'kP': 0.03,
            'kI': 0.00,
            'kD': 0.00,
            'kF': 0.00,
            'max': .2,
            'kToleranceDegrees' : 2.0,
        }
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
            self.rotation_output
        )
        #then, we set some parameters
        self.rotation_PID.setInputRange(0, 360)
        self.rotation_PID.setContinuous(True)
        self.rotation_PID.setOutputRange(-self.rotation_PID_vars['max'], self.rotation_PID_vars['max'])
        self.rotation_PID.setAbsoluteTolerance(self.rotation_PID_vars['kToleranceDegrees'])



        # # Define all the variables for controlling crosstrack
        # self.crosstrack_PID_vars = {
        #     'kP': 0.03,
        #     'kI': 0.00,
        #     'kD': 0.00,
        #     'kF': 0.00,
        #     'max': .2,
        #     'kTolerance' : 2.0,
        # }
        # #first, we need to instantiate our objects up above
        # self.crosstrack_output = PID_Output()
        # #then, we make the PID object
        # self.crosstrack_PID = wpilib.PIDController(
        #     self.crosstrack_PID_vars['kP'], 
        #     self.crosstrack_PID_vars['kI'], 
        #     self.crosstrack_PID_vars['kD'], 
        #     self.crosstrack_PID_vars['kF'], 
        #     self.visionCamera, 
        #     self.crosstrack_output
        # )
        # #then, we set some parameters
        # self.crosstrack_PID.setInputRange(-400, 400)
        # self.crosstrack_PID.setOutputRange(-self.crosstrack_PID_vars['max'], self.crosstrack_PID_vars['max'])
        # self.crosstrack_PID.setAbsoluteTolerance(self.rotation_PID_vars['kTolerance'])
        
   
    def disabledPeriodic(self):
        #this looks for data from the camera
        self.visionCamera.poll()

        print("Heading: "+self.rotation_source.pidGet())


    def autonomousInit(self):
        """This function is run once each time the robot enters autonomous mode."""
        #self.timer.reset()
        #self.timer.start()

    def autonomousPeriodic(self):
        """This function is called periodically during autonomous."""


    def teleopPeriodic(self):
        """This function is called periodically during operator control."""

        #first, let's get all the data from the joystick so we know what we are working with
        stick = {
            'x': -.5*self.joystick.getX(),
            'y': .5*self.joystick.getY(),
            'rot': -.4*self.joystick.getTwist(),
            'throttle': self.joystick.getThrottle(),
            'trigger_button': self.trigger_button.get(),
            'thumb_button': self.thumb_button.get(),
            'snap_angle_button': self.snap_angle_button.get(),
            'translate_only_button': self.translate_only_button.get(),
            'rotate_only_button': self.rotate_only_button.get(),
            'control_crosstrack_button': self.control_crosstrack_button.get(),
        }



        # ##TESTING!!##
        # #lets see if we can control to a direction
        # stick['x'] = 0
        # stick['y'] = 0
        # stick['rot'] = 0

        # if first time:
        #     currentAngle = self.rotation_source.pidGet()
        #     newAngle = currentAngle +30
        #     self.rotation_PID.setSetpoint(newAngle)
        #     self.rotation_PID.enable()
        # else:
        #     stick['rot'] = self.rotation_output.correction


        # #make this work, by tuning the PID parameters in rotation_PID_vars using this process
        # # https://frc-pdr.readthedocs.io/en/latest/control/pid_control.html#tuning-methods




        #print(stick)

        #if we are going to use the throttle input, we should do that first
        if self.useThrottle:
            stick['x'] = stick['x']*stick['throttle']/self.throttleMax
            stick['y'] = stick['y']*stick['throttle']/self.throttleMax
            stick['rot'] = stick['rot']*stick['throttle']/self.throttleMax


        #so, if we want to translate only, we need to zero out the input for twitsting
        if stick['translate_only_button']:
            stick['rot'] = 0
        #if we want to rotate only, we should zero out the x and y
        if stick['rotate_only_button']:  
            stick['x'] = 0
            stick['y'] = 0

        #set the solenoids based on the button
        self.panel_eject_solenoid.set(stick['trigger_button'])
        self.panel_retract_solenoid.set(stick['thumb_button'])

       
        #In order to snap to control, we need to find the angle we are currently at, then set the target angle 
            #to the closest target angle
        if stick['snap_angle_button']: 
            if not self.snappingToAngle:
                #this is the first time, so we need to set where to snap to
                angleError = 360 #start with a big error
                currentAngle = self.rotation_source.pidGet() #get the angle the same way the PID control will
                #for any angle that has a smaller error, set the setpoint to it
                for name,angle in self.target_angles.items():
                    if abs((currentAngle-angle)%360) < angleError:
                        print('Setting angle to '+str(angle)+' for '+name)
                        angleError = abs((currentAngle-angle)%360)
                        self.rotation_PID.setSetpoint(angle)
                self.rotation_PID.enable()
                self.snappingToAngle = True
            else:    
                stick['rot'] = self.rotation_output.correction

        else:
            #if we aren't snapping, we should reset this variable and turn off control
            self.snappingToAngle = False
            self.rotation_PID.disable()


        #for control crosstrack, we need to take the control signal from crosstrack PID
        # if stick['control_crosstrack_button']:  
        #     stick['x'] = self.crosstrack_output.correction

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









