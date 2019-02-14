#
# See the notes for the other physics sample
#


from pyfrc.physics import drivetrains
from pyfrc.physics.visionsim import VisionSim

from networktables.util import ntproperty


class PhysicsEngine(object):
    """
       Simulates a 4-wheel mecanum robot using Tank Drive joystick control 
    """
    target = ntproperty("/camera/target", (0.0, 0.0, 0.0)) #angle and distance

    def __init__(self, physics_controller):
        """
            :param physics_controller: `pyfrc.physics.core.Physics` object
                                       to communicate simulation effects to
        """

        self.physics_controller = physics_controller
        self.position = 0

        self.physics_controller.add_device_gyro_channel("navxmxp_i2c_1_angle")
        self.physics_controller.add_device_gyro_channel("navxmxp_spi_4_angle")


        targets = [
            #everything on the left side of the field
            VisionSim.Target(18.5, 12.5, 90, 270), # front cargo
            VisionSim.Target(0, 2, -90, 90), #  pickup station           
            VisionSim.Target(22, 11.25, 180, 360), # cargo side 1
            VisionSim.Target(23.75, 11.25, 180, 360), # cargo side 2
            VisionSim.Target(25.5, 11.25, 180, 360), # cargo side 3
            VisionSim.Target(17.5, 2, 90-29, 90-29+180), # rocket fromt
            VisionSim.Target(21, 2, -90+29, -90+29+180), # rocket back
      
            #everything on the left side of the field
            VisionSim.Target(18.5, 27-12.5, 90, 270), # front cargo
            VisionSim.Target(0, 27-2, -90, 90), #  pickup station           
            VisionSim.Target(22, 27-11.25, 0, 180), # cargo side 1
            VisionSim.Target(23.75, 27-11.25, 0, 180), # cargo side 2
            VisionSim.Target(25.5, 27-11.25, 0, 180), # cargo side 3
            VisionSim.Target(17.5, 27-2, 90+29, 90+29+180), # rocket fromt
            VisionSim.Target(21, 27-2, -90-29, -90-29+180), # rocket back

            VisionSim.Target(18.5, 14.5, 90, 270), # front right cargo

        ]

        self.vision = VisionSim(
            targets, 
            61.0, #camera FOV
            .1,  #close limit (ft)
            10,   #far limit (ft)
            15,  #update rate (hz)
            physics_controller=physics_controller
        )

        #Parameters: 
            # targets – List of target positions (x, y) on field in feet
            # view_angle_start – Center angle that the robot can ‘see’ the target from (in degrees)
            # camera_fov – Field of view of camera (in degrees)
            # view_dst_start – If the robot is closer than this, the target cannot be seen
            # view_dst_end – If the robot is farther than this, the target cannot be seen
            # data_frequency – How often the camera transmits new coordinates
            # data_lag – How long it takes for the camera data to be processed and make it to the robot
            # physics_controller – If set, will draw target information in UI

    def update_sim(self, hal_data, now, tm_diff):
        """
            Called when the simulation parameters for the program need to be
            updated.
            
            :param now: The current time as a float
            :param tm_diff: The amount of time that has passed since the last
                            time that this function was called
        """

        # Simulate the drivetrain
        # -> Remember, in the constructor we inverted the left motors, so
        #    invert the motor values here too!
        lr_motor = -hal_data["pwm"][1]["value"]
        rr_motor = hal_data["pwm"][3]["value"]
        lf_motor = -hal_data["pwm"][0]["value"]
        rf_motor = hal_data["pwm"][2]["value"]

        vx, vy, vw = drivetrains.mecanum_drivetrain(
            lr_motor, rr_motor, lf_motor, rf_motor
        )
        self.physics_controller.vector_drive(vx, -vy, vw, tm_diff)

        x, y, angle = self.physics_controller.get_position()
        data = self.vision.compute(now, x, y, angle)
        if data is not None:
            self.target = [data[0][0], data[0][2],12*data[0][3]]
