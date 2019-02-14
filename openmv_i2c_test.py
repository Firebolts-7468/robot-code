# Hello World Example
#
# Welcome to the OpenMV IDE! Click on the green run arrow button below to run the script!

import sensor, image, time, utime

from pyb import I2C

sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
clock = time.clock()                # Create a clock object to track the FPS.

i2c = I2C(2)
i2c.init(I2C.SLAVE, addr=4)

# print(devices)

started = False
i = 0
while(True):
    clock.tick()                    # Update the FPS clock.

    img = sensor.snapshot()         # Take a picture and return the image.
    # print(clock.fps())              # Note: OpenMV Cam runs about half as fast when connected

    if started == False:
        start = utime.ticks_ms()
        started = True
    if started and utime.ticks_diff(utime.ticks_ms(), start) > 1000:
        i2c.send('hello')
        i += 1
        started = False
