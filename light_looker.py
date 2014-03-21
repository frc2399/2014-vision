from __future__ import division

import cv2
import cv2.cv as cv

import numpy as np

import time, sys, subprocess, os

import nt_client
import webcam



# Enable graphical debug mode, including viewing windows
# For testing make DEBUG = True and ROBOT = False
# For actual use make DEBUG = False and ROBOT = True
DEBUG = True

GPIO_DELAY = 0.05
RED_LED = 11
GREEN_LED = 13
BLUE_LED = 15

CAPTURE_WIDTH = 320
CAPTURE_HEIGHT = 240

CAMERA_ID = 0

BLUR = (2, 2)

EXPOSURE_LEVEL = 5000


# Auto detect if we have GPIO (if we are running on an actual Pi)
try:
    import RPi.GPIO as GPIO
    USE_GPIO = True
except ImportError:
    USE_GPIO = False
    pass

# Auto detect if we are running in X or not
if os.environ.get('DISPLAY', ''):
    USE_DISPLAY = True
else:
    USE_DISPLAY = False


# Auto detect if we are running on the robot or not
retcode = subprocess.call(['ping', '10.23.99.2', '-c', '-1'])
if retcode == 0:    
    ROBOT = True
else:
    ROBOT = False


def set_exposure(level):
    'Sets a webcam to use manual exposure control'
    # Camera parameter control - force manual exposure
    # uvcdynctrl -s 'Exposure, Auto' 1
    # uvcdynctrl -s 'Exposure (Absolute)' 1058
    # Higher exposure numbers result in darker images
    subprocess.call('uvcdynctrl -s "Exposure, Auto" %s' % 1, shell=True)
    subprocess.call('uvcdynctrl -s "Exposure (Absolute)" %s' % level, shell=True)


def get_cap():
    'Initializes and returns the VideoCapture object'
    cap = cv2.VideoCapture(CAMERA_ID)
    
    #cap.set(cv.CV_CAP_PROP_CONVERT_RGB, False)
    cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)
    cap.set(cv.CV_CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
    #cap.set(cv.CV_CAP_PROP_EXPOSURE, 430)
    #cap.set(cv.CV_CAP_PROP_FPS, 25)
    
    return cap

#This method skips frames on the camera
def skip_frames(cap, n):
    'Skips n frames on a VideoCapture device'
    for i in range(n):
        cap.read()

#This method sets the LEDs on or off
def set_leds(x):
    'Turns LEDs on or off (True is on, False is off)'
    for led in [RED_LED, GREEN_LED, BLUE_LED]:

        GPIO.output(led, x)
        
#This method provides us with a smooth shutdown via a joystick button
def shutdown():
    if USE_GPIO:
        set_leds(True)
    os.system("sudo shutdown -h now")
    exit(0)

#This method sets up the aspect ratios of a rectangle
def aspect_ratio(rectangle):
    x, y, w, h = rectangle
    return w/h

#This method tells us if a rectangle is a static target or not
def is_static_target(rect):
    ar = aspect_ratio(rect)
    #originally 0.2 and 0.15
    if ar <= 0.25 and ar >= 0.10:
        return True
    else:
        return False

#This method tells us if a rectangle is a dynamic rectangle or not
def is_dynamic_target(rect):
    ar = aspect_ratio(rect)
    print "AR: ", ar
    #originally 5.45 and 4.5
    if ar <= 6 and ar >= 3:
        return True
    else:
        return False

#This method tells us the area of a rectangle 
def area(rect):
    x, y, w, h = rect
    return w*h

#This method tells us if the camera has detected the static and dynamic targets
#Also if their ratios are within the min and max range
def are_target_pair(rect1, rect2):
    ratio = area(rect1) / area(rect2)
    if is_static_target(rect1) and is_dynamic_target(rect2) and ratio >= 1.2 and ratio <= 1.95:
        return True
    else:
        return False

def main():
    if USE_GPIO:
        GPIO.cleanup()
        #this sets up the LEDs on the GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(RED_LED, GPIO.OUT)
        GPIO.setup(GREEN_LED, GPIO.OUT)
        GPIO.setup(BLUE_LED, GPIO.OUT)

    #Self explanatory but this sets the exposure to the level we want it 
    set_exposure(EXPOSURE_LEVEL)

    if USE_DISPLAY:
        cv2.namedWindow('original', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('rectangles', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('difference', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('threshold', cv2.WINDOW_AUTOSIZE)

    cap = get_cap()

    #This connects the pi to the Network Tables
    if ROBOT:
        client = nt_client.NetworkTableClient("2399")

    frames = 0

    start_time = time.time()
    
    frame1 = np.empty(shape=(CAPTURE_HEIGHT, CAPTURE_WIDTH, 3), dtype=np.uint8)
    frame2 = np.empty(shape=(CAPTURE_HEIGHT, CAPTURE_WIDTH, 3), dtype=np.uint8)
    
    #gray1 = np.empty(shape=(CAPTURE_HEIGHT, CAPTURE_WIDTH), dtype=np.uint8)
    #gray2 = np.empty(shape=(CAPTURE_HEIGHT, CAPTURE_WIDTH), dtype=np.uint8)
    
    blur1 = np.empty(shape=(CAPTURE_HEIGHT, CAPTURE_WIDTH), dtype=np.uint8)
    blur2 = np.empty(shape=(CAPTURE_HEIGHT, CAPTURE_WIDTH), dtype=np.uint8)
    
    mask = np.empty(shape=(CAPTURE_HEIGHT, CAPTURE_WIDTH), dtype=np.uint8)
    
    diff = np.empty(shape=(CAPTURE_HEIGHT, CAPTURE_WIDTH), dtype=np.uint8)
    bw = np.empty(shape=(CAPTURE_HEIGHT, CAPTURE_WIDTH), dtype=np.uint8)
    
    webcam.start_server()

    while True:
        if ROBOT:
            if client.getValue("/Vision/shutdown") == 1:
                shutdown()

        if USE_GPIO:
            set_leds(True)
            time.sleep(GPIO_DELAY)

        #print "fps = ", cap.get(cv.CV_CAP_PROP_FPS)
        #print "saturation = ", cap.get(cv.CV_CAP_PROP_SATURATION)
        #print "exposure = ", cap.get(cv.CV_CAP_PROP_EXPOSURE)

        skip_frames(cap, 4)
        #ret, img = cap.read(frame1)
        ret, frame1 = cap.read()
        clock_start = time.clock()
        
        if USE_GPIO:
            set_leds(False)
            time.sleep(GPIO_DELAY)

        #print "fps = ", cap.get(cv.CV_CAP_PROP_FPS)
        #print "saturation = ", cap.get(cv.CV_CAP_PROP_SATURATION)
        #print "exposure = ", cap.get(cv.CV_CAP_PROP_EXPOSURE)

        skip_frames(cap, 4)
        ret, frame2 = cap.read()
        clock_end = time.clock()
        
        #webcam.update_image(frame2)

        #this converts the images to greyscale
        gray1 = cv2.cvtColor(frame1, cv.CV_RGB2GRAY)
        gray2 = cv2.cvtColor(frame2, cv.CV_RGB2GRAY)

        #increases brightness on frame2
        frame2 = frame2 * 5.0
        frame2 = np.clip(frame2, 0, 255)
        frame2 = np.array(frame2, dtype = np.uint8)

        #this blurs the images
        blur1 = cv2.blur(gray1, BLUR)
        blur2 = cv2.blur(gray2, BLUR)
        
        # create a mask around the bright light of frame1
        #cv2.adaptiveThreshold(blur1, 50, cv.CV_ADAPTIVE_THRESH_GAUSSIAN_C,
        #                      cv.CV_THRESH_BINARY, 5, 0, mask)
        #cv2.threshold(blur1, 190, 255, cv2.THRESH_BINARY, mask)

        #this takes the difference of the two images
        diff = cv2.subtract(blur1, blur2)

        #this converts the image to black and white (threshold)
        #cv2.adaptiveThreshold(diff, 50, cv.CV_ADAPTIVE_THRESH_GAUSSIAN_C,
        #                      cv.CV_THRESH_BINARY, 5, 0, bw)
        # src, thresh, maxValue, type
        retval, bw = cv2.threshold(diff, 95, 255, cv2.THRESH_BINARY)

        contimg = bw.copy()

        contours, hierarchy = cv2.findContours(contimg, 1, 2)
        contours.sort(key = cv2.contourArea, reverse = True)


        #This tells us if we've found a pair of rectangles
        found_pair = False
        found_static = False
        if len(contours) >= 2:
            for i in range(len(contours)):
                cnt1 = contours[i]
                for j in range(i + 1, len(contours)):
                    cnt2 = contours[j]
                    if are_target_pair(cv2.boundingRect(cnt1), cv2.boundingRect(cnt2)):
            
                        x, y, w1, h1 = cv2.boundingRect(cnt1)
                        cv2.rectangle(contimg, (x,y), (x+w1, y+h1), 200)
                        cv2.rectangle(frame2, (x,y), (x+w1, y+h1), (0, 255, 0))
                        x, y, w2, h2 = cv2.boundingRect(cnt2)
                        cv2.rectangle(contimg, (x,y), (x+w2, y+h2), 200)
                        cv2.rectangle(frame2, (x,y), (x+w2, y+h2), (0, 255, 0))
                        dist = 20726 * h1 **(-1.138)
                        webcam.update_image(frame2)

                        if ROBOT:
                            
                            client.setValue("/Vision/distance", dist)
                            
                            
                        print dist

                        found_pair = True
                        print "hot"
                        
                        if ROBOT:
                            
                            client.setValue("/Vision/hot", True)
                            
                        break
                    
                if found_pair:
                    break
        if not found_pair:       
            print "not"
            
            if ROBOT:
                
                client.setValue("/Vision/hot", False)
                
        if not found_pair and len(contours) >= 1:
            for i in range(len(contours)):
                cnt1 = contours[i]
                if is_static_target(cv2.boundingRect(cnt1)):
                    x, y, w1, h1 = cv2.boundingRect(cnt1)
                    cv2.rectangle(contimg, (x,y), (x+w1, y+h1), 200)
                    cv2.rectangle(frame2, (x,y), (x+w1, y+h1), (0, 255, 0))
                    dist = 20726 * h1 **(-1.138)
                    webcam.update_image(frame2)

                    if ROBOT:
                            
                        client.setValue("/Vision/distance", dist)
                            
                            
                    print dist
                    found_static = True
                    break
                
        if not found_static:
            webcam.update_image(frame2)
        

            #This finds rectangle contours
##            cnt1 = contours[0]
##            cnt2 = contours[1]
##            rect = cv2.boundingRect(cnt1)
##            
##            x, y, w1, h1 = cv2.boundingRect(cnt1)
##            cv2.rectangle(contimg, (x,y), (x+w1, y+h1), 200)
##            x, y, w2, h2 = cv2.boundingRect(cnt2)
##            cv2.rectangle(contimg, (x,y), (x+w2, y+h2), 200)
##            area1 = cv2.contourArea(cnt1)
##            area2 = cv2.contourArea(cnt2)
##
##            dist = 20726 * h1 **(-1.138)
##
##            if ROBOT:
##                
##                client.setValue("/Vision/distance", dist)
##                
##                
##            print dist 
        #print w1, h1, w2, h2

        #M = cv2.moments(cnt1)
        #M2 = cv2.moments(cnt2)

        #print M

        #masked = cv2.bitwise_and(diff, mask)
        
        if USE_DISPLAY:
            cv2.imshow('original', frame1)
            cv2.imshow('rectangles', contimg)
            cv2.imshow('difference', diff)
            cv2.imshow('threshold', bw)
        
        c = cv2.waitKey(25)
        if c == 27:
            if USE_GPIO:
                GPIO.cleanup()
            exit(0)



        
#        if DEBUG:
#            print "Frame %d\t%.3fs\r" % (frames, (clock_end - clock_start)),
#            sys.stdout.flush()
#            frames += 1
#
#            if frames % 10 == 0:
#                print "\n"
#                currtime = time.time()
#                numsecs = currtime - start_time
#                fps = frames / numsecs
#                print "average FPS:", fps



if __name__ == '__main__':
    try:
        main()
    except:
        if USE_GPIO:
            GPIO.cleanup()
        import traceback
        traceback.print_exc()
