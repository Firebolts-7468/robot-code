# Single Color Grayscale Blob Tracking Example
#
# This example shows off single color grayscale tracking using the OpenMV Cam.

import sensor, image, time, utime

import ustruct as struct
from pyb import I2C
import pyb


sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QVGA)  # 320×240
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
sensor.set_auto_exposure(False, exposure_us = int(60))
clock = time.clock()


#setting up the i2c communication
i2c = I2C(2)
i2c.init(I2C.SLAVE, addr=4)

# Only blobs that with more pixels than "pixel_threshold" and more area than "area_threshold" are
# returned by "find_blobs" below. Change "pixels_threshold" and "area_threshold" if you change the
# camera resolution. "merge=True" merges all overlapping blobs in the image.

started = False
i = 0
while(True):
    clock.tick()
    # Take a picture
    img = sensor.snapshot()


    #region of interest, only looks where we know targets might be, this does the whole width, but only the top 75%
    roi = [0,0,img.width(),int(.75*img.height())]

    #x_stride and y_stride will make searching faster, we just need to know how big the blobs are
    x_stride = 5
    y_stride = 5

    # The below grayscale threshold is set to only find extremely bright white areas.
    thresholds = (65, 255)
    # Find all the "blobs"
    blobs = img.find_blobs([thresholds],roi=roi, x_stride=x_stride, y_stride=y_stride, pixels_threshold=100, area_threshold=100, merge=True)
    print (len(blobs))
    # IF there's two blobs and they're rotated at the right angle, then figure out where the target is
    if len(blobs) >= 2:
        #sort the blob list so that the biggest blobs are at the start of the list
        blobs.sort(key=lambda blob: blob.area(), reverse=True)
        if (((blobs[0]).rotation()*180/3.14 > 90) and ((blobs[1]).rotation()*180/3.14 < 90)) \
        or (((blobs[0]).rotation()*180/3.14 < 90) and ((blobs[1]).rotation()*180/3.14 > 90)):

            # Draw where we think the rectangles are
            for blob in blobs[:2]:
                img.draw_rectangle(blob.rect(), thickness=5)
                img.draw_cross(blob.cx(), blob.cy())
                #print(blob.area())
               # print(blob.rotation()*180/3.14)

            # Calculate the distance between the two blobs in pixels
            distance = abs(blobs[0].cx() - blobs[1].cx())
            #calculate the distance to the target (in inces)
            to_target = -(distance - 390) / 5.8

            #find the point in the center of the two blobs, in pixels from center of image
            center = (blobs[0].cx() + blobs[1].cx()) / 2 - img.width() / 2
            # print(center)

            #All of this code works to only send a message every second
            if started == False:
                start = utime.ticks_ms()
                started = True
            if started and utime.ticks_diff(utime.ticks_ms(), start) > 1000:
                #actually sends the message to the robot, center and distance
                i2c.send(struct.pack('<ii', int(center), int(distance)))
                print('SEND: %i' % center)
                i += 1
                started = False

            #find the rotation of the robot

           # print( to_target)
            #print(blobs[0].pixels())
#            #print(center)
            #print(img.width())
            #angle_1 = blobs[1].rotation()
            #angle_0 = blobs[0].rotation()
            #print(angle_1)
            #print(angle_0)

            # to do (first two are done):
            # 1) how far away is the target? (sort of done, see "distance")
            # 2) where is the target? (done for left/right: "center")
            # 3) what angle is the target? (should we rotate the robot?)

#    else: print( len(blobs))
       # if (blob[1]).rotation()*180/3.14 > 90:
#    for blob in img.find_blobs([thresholds], pixels_threshold=100, area_threshold=100, merge=True):
        #img.draw_rectangle(blob.rect(), thickness=5)
        #img.draw_cross(blob.cx(), blob.cy())
 #       if blob.rotation()*180/3.14 < 90:
  #          print("red")
   #     if blob.rotation()*180/3.14 >90:
    #        print("blue")

        #print(blob.rotation()*180/3.14)
        #color blobs with positive angle blue
        #color blobs with negative angle red
        #if we have one positive on the left, and one negative on the right, color them both green
