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

machine = os.uname().machine

if os.uname().machine == 'armv7l':
    print("Success -- import ctre library")
    import ctre
else:
    print("Warning: ctre library not imported (ctre only supported on the RoboRIO)")

class MyRobot(wpilib.TimedRobot):
    def initTalonFX(self, talon,
        kF=0.3,
        kP=0.1,
        kI=0,
        kD=0,
        inverted=False,
        enCurrentLimit=False,
        statorCurrentLimit=2.0,
        supplyCurrentLimit=1.0):

        talon.configFactoryDefault()
        
        # /* Config neutral deadband to be the smallest possible */
        talon.configNeutralDeadband(0.001)

        # /* Config sensor used for Primary PID [Velocity] */
        talon.configSelectedFeedbackSensor(ctre.TalonFXFeedbackDevice.IntegratedSensor, 0, 10)

        #talon.setSensorPhase(inverted)

        talon.setInverted(inverted)

        # /* Config the peak and nominal outputs */
        talon.configNominalOutputForward(0, 10)
        talon.configNominalOutputReverse(0, 10)
        talon.configPeakOutputForward(1, 10)
        talon.configPeakOutputReverse(-1, 10)

        talon.configAllowableClosedloopError(0, 0, 10);

        # /* Config the Velocity closed loop gains in slot0 */
        talon.config_kF(0, kF, 10)
        talon.config_kP(0, kP, 10)
        talon.config_kI(0, kI, 10)
        talon.config_kD(0, kD, 10)
        '''
        * Configure the current limits that will be used
          * Stator Current is the current that passes through the motor stators.
          *  Use stator current limits to limit rotor acceleration/heat production
          * Supply Current is the current that passes into the controller from the supply
          *  Use supply current limits to prevent breakers from tripping
          *
          *  enabled | Limit(amp) | Trigger Threshold(amp) | Trigger Threshold Time(s)  */
        '''
        #talon.configStatorCurrentLimit(ctre.StatorCurrentLimitConfiguration(enCurrentLimit, statorCurrentLimit, statorCurrentLimit*1.5, 0.05))
        #talon.configSupplyCurrentLimit(ctre.SupplyCurrentLimitConfiguration(enCurrentLimit, supplyCurrentLimit, supplyCurrentLimit*1.5, 0.05))

    def setShooterHoodPos(self, pos):
        # pos 0 - 1
        pos_cmd = pos * self.hoodCtsPerRot / 4.0

        self.shooterHoodCAN.set(mode=ctre.ControlMode.Position, value=pos_cmd)

    def robotInit(self):
        """
        This function is called upon program startup and
        should be used for any initialization code.
        """

        # Talon CAN motor init
        '''
        Talon closed loop control guide
        https://phoenix-documentation.readthedocs.io/en/latest/ch16_ClosedLoop.html

        Talon (CTRE) Python API documentation
        https://robotpy.readthedocs.io/projects/ctre/en/latest/api.html

        Talon example code (Java and C++)
        https://github.com/CrossTheRoadElec/Phoenix-Examples-Languages

        ## One-time setup for each Talon
        Use the diagnostics tool in Windows to:
            1. Update the FW
            2. Set the ID number
            3. Write the ID down somewhere (ideally, label the motor)
            4. Use the Self-Test Snapshot and Plot to make sure the motor works

        NOTE: MOTOR POSITION CONTROL IS EXTREMELY DANGEROUS RIGHT NOW
            NEVER USE POSITION CONTROL WITHOUT CURRENT LIMIT
            NEVER USE POSITION CONTROL WITHOUT SUPERVISION + E-STOP READINESS
            Look into limit switches for motor auto-shutoff
        '''

        self.shooterCAN = ctre.TalonFX(6)
        self.initTalonFX(self.shooterCAN)

        self.shooterCANfollow = ctre.TalonFX(1)
        self.initTalonFX(self.shooterCANfollow, inverted=True)
        self.shooterCANfollow.set(mode=ctre.ControlMode.Follower, value=6)



        self.shooterHoodCAN = ctre.TalonFX(5)
        self.initTalonFX(self.shooterHoodCAN)
        #self.initTalonFX(self.shooterHoodCAN, kF=0, kP=0.02, kI=0, inverted=True, enCurrentLimit=True)
        #self.shooterHoodCAN.setSelectedSensorPosition(0, 0, 10)





        #Get information from network tables
        NetworkTables.initialize()
        self.sd = NetworkTables.getTable("SmartDashboard")
        self.lime = NetworkTables.getTable("limelight")






        #Set up all the motor controllers 
        self.leftDriveCAN = ctre.WPI_TalonFX(13)
        # self.initTalonFX(self.leftDriveCAN)
        self.leftDriveCANfollow = ctre.TalonFX(12)
        # self.initTalonFX(self.leftDriveCANfollow)
        self.leftDriveCANfollow.set(mode=ctre.ControlMode.Follower, value=13)

        self.rightDriveCAN = ctre.WPI_TalonFX(11)
        # self.initTalonFX(self.rightDriveCAN)
        self.rightDriveCANfollow = ctre.TalonFX(10)
        # self.initTalonFX(self.rightDriveCANfollow)
        self.rightDriveCANfollow.set(mode=ctre.ControlMode.Follower, value=11)
        

        self.indexerMotorCAN = ctre.VictorSPX(9)
        self.intakeMotorCAN = ctre.VictorSPX(8)

        self.leftClimbCAN = ctre.VictorSPX(15)
        self.rightClimbCAN = ctre.VictorSPX(14)

        
    


        #Set up the drivetrain motors. 
        self.drive = wpilib.drive.DifferentialDrive(self.leftDriveCAN, self.rightDriveCAN)
    
        self.intakeOn = False
        self.indexerOn = False
        self.shooterOn = False
        self.hoodOn = False

        self.cycleCount = 0

        self.hoodDirection = 'stopped'  #stopped, forward, backward
        self.currentHoodPos = 0
        self.hoodSlop = .5
        self.zeroHood = False
        self.hoodSpeed = .05

        self.hoodCtsPerRot = 2048 * 70.0 # counts per rotation * gear reduction / quadrature?

        self.joystick = wpilib.XboxController(0)

        self.indexerTimer = wpilib.Timer()
        self.indexerTimer.start()

        self.shooterTimer = wpilib.Timer()
        self.shooterTimer.start()

        self.hoodTimer = wpilib.Timer()
        self.hoodTimer.start()

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
        
        #self.setShooterHoodPos(0.5)
        #print("err: %s" % self.shooterHoodCAN.getClosedLoopError(0))
        #print("pos: %s" % self.shooterHoodCAN.getSelectedSensorPosition(0))

        self.cycleCount+=1
        #first, let's get some inofrmation from our control station, we default to not moving
        xScale = self.sd.getNumber("xScale",0)
        yScale = self.sd.getNumber("yScale",0)
        spinScale = self.sd.getNumber("spinScale",0)
        climbScale = self.sd.getNumber("climbScale",0)
        steeringTrim = self.sd.getNumber("steeringTrim",-0.005)
        
        intakeSpeed = self.sd.getNumber("intakeSpeed",0)
        indexerSpeed = self.sd.getNumber("indexerSpeed",0)
        shooterSpeed = self.sd.getNumber("shooterSpeed",0)
        hoodPosition = self.sd.getNumber("hoodPosition",0)

        intakeState = self.sd.getString("intakeState","off")
        indexerState = self.sd.getString("indexerState","off")
        shooterState = self.sd.getString("shooterState","off")
        climbState = self.sd.getString("climbState","normal")
        hoodState = self.sd.getString("hoodState","off")

        visionP = self.sd.getNumber("visionP",0.025)
        rpmTarget = self.sd.getNumber("rpmTarget",-1)
        launchAngleTarget = self.sd.getNumber("launchAngleTarget",-1)


        #here we get the current aiming of the vision system 
        limeTx = self.lime.getNumber("tx",0)
        limeTy = self.lime.getNumber("ty",0)

        #just print out some stuff for debug
        #if self.cycleCount%200==0:
        #    print(str(xScale)+' '+str(yScale)+' '+str(shooterSpeed))


        #get values from joystick
        yvalue =  self.joystick.getY(wi.GenericHID.Hand.kLeftHand)
        xvalue =  self.joystick.getX(wi.GenericHID.Hand.kRightHand)
        leftTrigger = self.joystick.getTriggerAxis(wi.GenericHID.Hand.kLeftHand)
        rightTrigger = self.joystick.getTriggerAxis(wi.GenericHID.Hand.kRightHand)

        # yvalue =  -self.joystick.getY(1)
        # xvalue =  self.joystick.getX(0)
        # leftTrigger = self.joystick.getTriggerAxis(0)
        # rightTrigger = self.joystick.getTriggerAxis(1)
    
        
        #####DRIVE#####

        #look to see if the user wants to spin
        if leftTrigger > .1 or rightTrigger >.1:
            self.drive.curvatureDrive(yvalue*yScale, (-leftTrigger+rightTrigger)*spinScale+steeringTrim, True)
        #Use the A button to spin the robot to look at the target
        elif self.joystick.getAButton():
            if limeTx>5: limeTx=5
            if limeTx<-5: limeTx=-5
            self.drive.curvatureDrive(0, limeTx*visionP, True)
        #else, just drive normally
        else:
            self.drive.curvatureDrive(yvalue*yScale, xvalue*xScale+steeringTrim, False)
        



        #####HOOD#####

        #If the hood is moving, we need to update its position
        # if self.hoodDirection == 'forward':
        #     self.currentHoodPos += self.hoodSpeed*self.hoodTimer.get()
        # elif self.hoodDirection == 'backward':
        #     self.currentHoodPos -= self.hoodSpeed*self.hoodTimer.get()
        # self.hoodTimer.reset()


        # if hoodState == 'on' or hoodState == 'auto':
        #     if self.hoodOn == False:
        #         if self.hoodSwitch.get() == False:
        #             self.hoodDirection = 'backward'
        #             self.hoodMotor.set(-self.hoodSpeed)
        #     else:
        #         if self.currentHoodPos < hoodPosition-self.hoodSlop:
        #             #drive the hood forward
        #             self.hoodDirection = 'forward'
        #             self.hoodMotor.set(self.hoodSpeed)
        #         elif self.currentHoodPos > hoodPosition+self.hoodSlop:
        #             #drive the hood forward
        #             self.hoodDirection = 'backward'
        #             self.hoodMotor.set(-self.hoodSpeed)
        #         else:
        #             self.hoodDirection = 'stopped'
        #             self.hoodMotor.set(0)
        # else:
        #     self.hoodMotor.set(0)

        # #last, take care of a limit switch
        # if self.hoodSwitch.get():
        #     #means the switch is pressed
        #     self.hoodDirection = 'stopped'
        #     self.currentHoodPos = 0

            



        #####BUTTONS#####

        #toggle intake using Y button
        if self.joystick.getYButtonPressed():
            self.intakeOn = not self.intakeOn

        #toggle indexer on and off
        if self.joystick.getXButtonPressed():
            if not self.shooterOn:
                self.shooterOn = True
                self.shooterTimer.reset()
                #self.hoodOn = True
            else:
                self.indexerOn = True
                self.indexerTimer.reset()

    

        if self.indexerOn and self.indexerTimer.hasPeriodPassed(1):
            self.indexerOn = False

        #toggle shooter on and off
        #if self.joystick.getBButtonPressed():
        if self.joystick.getBButton():
            #turn off shooter
            self.shooterOn = False
            #return hood
            self.hoodOn = False



        #####SUB SYSTEM CONTROL########

        #based on input from control panel, and from joystick, turn stuff on and off
        if intakeState == "on" or (intakeState == "controller" and self.intakeOn): 
            self.intakeMotorCAN.set(mode=ctre.ControlMode.PercentOutput, value=intakeSpeed)
        else:
            self.intakeMotorCAN.set(mode=ctre.ControlMode.PercentOutput, value=0)

        if indexerState == "on" or (indexerState == "controller" and self.indexerOn): 
            self.indexerMotorCAN.set(mode=ctre.ControlMode.PercentOutput, value=indexerSpeed)
        else:
            self.indexerMotorCAN.set(mode=ctre.ControlMode.PercentOutput, value=0)

        if shooterState == "on" or (shooterState == "controller" and self.shooterOn) or (shooterState == "auto" and self.shooterOn): 
            if self.shooterTimer.get()>4:
                self.shooterCAN.set(mode=ctre.ControlMode.PercentOutput, value=shooterSpeed)
            elif self.shooterTimer.get()>2:
                self.shooterCAN.set(mode=ctre.ControlMode.PercentOutput, value=shooterSpeed*.5)
            elif self.shooterTimer.get()>1:
                self.shooterCAN.set(mode=ctre.ControlMode.PercentOutput, value=shooterSpeed*.25)
            else:
                self.shooterCAN.set(mode=ctre.ControlMode.PercentOutput, value=shooterSpeed*.1)

        else:
            self.shooterCAN.set(mode=ctre.ControlMode.PercentOutput, value=0)


        #####CLIMB######

        # if self.joystick.getBumper(wi.GenericHID.Hand.kLeftHand):
        #     if climbState == 'normal':
        #         self.leftClimbCAN.set(mode=ctre.ControlMode.PercentOutput, value=climbScale)
        #     if climbState == 'retract':
        #         self.leftClimbCAN.set(mode=ctre.ControlMode.PercentOutput, value=-climbScale)
        # else:
        #     self.leftClimbCAN.set(mode=ctre.ControlMode.PercentOutput, value=0)

        # if self.joystick.getBumper(wi.GenericHID.Hand.kRightHand):
        #     if climbState == 'normal':
        #         self.rightClimbCAN.set(mode=ctre.ControlMode.PercentOutput, value=climbScale)
        #     if climbState == 'retract':
        #         self.rightClimbCAN.set(mode=ctre.ControlMode.PercentOutput, value=-climbScale)
        # else:
        #     self.rightClimbCAN.set(mode=ctre.ControlMode.PercentOutput, value=0)
     

        if self.joystick.getBumper(wi.GenericHID.Hand.kLeftHand):
            self.shooterHoodCAN.set(mode=ctre.ControlMode.PercentOutput, value=hoodSpeed*.1)
        elif self.joystick.getBumper(wi.GenericHID.Hand.kRightHand):
            self.shooterHoodCAN.set(mode=ctre.ControlMode.PercentOutput, value=-hoodSpeed*.1)
        else:
            self.shooterHoodCAN.set(mode=ctre.ControlMode.PercentOutput, value=0)

       


        #self.drive.arcadeDrive(yvalue/joystickYScale, xvalue/joystickXScale, squareInputs=True)

        #print(yvalue/joystickYScale)

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
        #     self.indexerMotorCAN.set(0.3)
        # else:
        #     self.indexerMotorCAN.set(0)


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






