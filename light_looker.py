import cv2
import cv2.cv as cv

import numpy as np

import time, sys, subprocess
import os


try:
    import RPi.GPIO as GPIO
    USE_GPIO = True
except ImportError:
    USE_GPIO = False
    pass


# Enable graphical debug mode, including viewing windows
DEBUG = False
ROBOT = True

GPIO_DELAY = 0.05
RED_LED = 11
GREEN_LED = 13
BLUE_LED = 15

CAPTURE_WIDTH = 320
CAPTURE_HEIGHT = 240

CAMERA_ID = 0

BLUR = (2, 2)

EXPOSURE_LEVEL = 5000

if ROBOT:
    
    import nt_client

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


def skip_frames(cap, n):
    'Skips n frames on a VideoCapture device'
    for i in range(n):
        cap.read()


def set_leds(x):
    'Turns LEDs on or off (True is on, False is off)'
    for led in [RED_LED, GREEN_LED, BLUE_LED]:

        GPIO.output(led, x)

def shutdown():
    if USE_GPIO:
        set_leds(True)
    os.system("sudo shutdown -h now")
    exit(0)


def main():
    if USE_GPIO:
        GPIO.cleanup()
        #this sets up the LEDs on the GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(RED_LED, GPIO.OUT)
        GPIO.setup(GREEN_LED, GPIO.OUT)
        GPIO.setup(BLUE_LED, GPIO.OUT)
    
    set_exposure(EXPOSURE_LEVEL)

    if DEBUG:
        cv2.namedWindow('a', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('b', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('c', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('d', cv2.WINDOW_AUTOSIZE)

    cap = get_cap()
    
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
        
        #this converts the images to greyscale
        gray1 = cv2.cvtColor(frame1, cv.CV_RGB2GRAY)
        gray2 = cv2.cvtColor(frame2, cv.CV_RGB2GRAY)

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
        retval, bw = cv2.threshold(diff, 40, 255, cv2.THRESH_BINARY)

        contimg = bw.copy()

        contours, hierarchy = cv2.findContours(contimg, 1, 2)
        contours.sort(key = cv2.contourArea, reverse = True)

        if len(contours) >= 2:
             
            cnt1 = contours[0]
            cnt2 = contours[1]
            x, y, w1, h1 = cv2.boundingRect(cnt1)
            cv2.rectangle(contimg, (x,y), (x+w1, y+h1), 200)
            x, y, w2, h2 = cv2.boundingRect(cnt2)
            cv2.rectangle(contimg, (x,y), (x+w2, y+h2), 200)
            area1 = cv2.contourArea(cnt1)
            area2 = cv2.contourArea(cnt2)

            dist = 20726 * h1 **(-1.138)

            if ROBOT:
                
                client.setValue("/Vision/distance", dist)
                
                
            print dist 
        #print w1, h1, w2, h2

        #M = cv2.moments(cnt1)
        #M2 = cv2.moments(cnt2)

        #print M

        #masked = cv2.bitwise_and(diff, mask)
        
        if DEBUG:
            cv2.imshow('a', frame1)
            cv2.imshow('b', contimg)
            cv2.imshow('c', diff)
            cv2.imshow('d', bw)
        
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
