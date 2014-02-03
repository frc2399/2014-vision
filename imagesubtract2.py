import cv2
import cv2.cv as cv
import time
import subprocess
import RPi.GPIO as GPIO


GPIO_DELAY = 0.05

GPIO.cleanup()

# Camera parameter control - force manual exposure
# uvcdynctrl -s 'Exposure, Auto' 1
# uvcdynctrl -s 'Exposure (Absolute)' 1058
# Higher exposure numbers result in darker images
subprocess.call('uvcdynctrl -s "Exposure, Auto" %s' % 1, shell=True)
subprocess.call('uvcdynctrl -s "Exposure (Absolute)" %s' % 1058, shell=True)


cv2.namedWindow('a', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('b', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('c', cv2.WINDOW_AUTOSIZE)


cap = cv2.VideoCapture(0)

cap.set(cv.CV_CAP_PROP_CONVERT_RGB, False)
cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv.CV_CAP_PROP_FRAME_WIDTH, 320)
#cap.set(cv.CV_CAP_PROP_EXPOSURE, 430)
#cap.set(cv.CV_CAP_PROP_FPS, 25)

frames = 0

start_time = time.time()

#change numbers when we have LEDs to test with
#this sets up the LEDs on the GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)

def skip_frames(cap, n):
    for i in range(n):
        cap.read()


while True:
    #this turns the LEDs on
    GPIO.output(11, True)
    GPIO.output(13, True)
    GPIO.output(15, True)
    time.sleep(GPIO_DELAY)

    #print "fps = ", cap.get(cv.CV_CAP_PROP_FPS)
    #print "saturation = ", cap.get(cv.CV_CAP_PROP_SATURATION)
    #print "exposure = ", cap.get(cv.CV_CAP_PROP_EXPOSURE)

    # grab 2 frames before continuing
    skip_frames(cap, 3)
    retval, frame1 = cap.read()
    clock_start = time.clock()
    
    #this turns the LEDs off
    GPIO.output(11, False)
    GPIO.output(13, False)
    GPIO.output(15, False)
    time.sleep(GPIO_DELAY)

    #print "fps = ", cap.get(cv.CV_CAP_PROP_FPS)
    #print "saturation = ", cap.get(cv.CV_CAP_PROP_SATURATION)
    #print "exposure = ", cap.get(cv.CV_CAP_PROP_EXPOSURE)

    # grab 2 frames before continuing
    skip_frames(cap, 4)
    retval, frame2 = cap.retrieve()
    clock_end = time.clock()
    print "Time between on/off: %.3fs" % (clock_end - clock_start)

    #this converts the images to greyscale
    grey1 = cv2.cvtColor(frame1, cv.CV_RGB2GRAY)
    grey2 = cv2.cvtColor(frame2, cv.CV_RGB2GRAY)

    #this blurs the images
    #blur1 = cv2.blur(grey1, (5, 5))
    #blur2 = cv2.blur(grey2, (5, 5))

    #this takes the difference of the two images
    diff = cv2.absdiff(grey1, grey2)

    #this converts the image to black and white (threshold)
    #bw = cv2.adaptiveThreshold(diff, 50, cv.CV_ADAPTIVE_THRESH_GAUSSIAN_C, cv.CV_THRESH_BINARY, 5, 0)

    cv2.imshow('a', frame1)
    cv2.imshow('b', frame2)
    cv2.imshow('c', diff)

    c = cv2.waitKey(50)
    if c == 27:
        GPIO.cleanup()
        exit(0)

    print "Frame", frames
    frames += 1

    if frames % 10 == 0:
        currtime = time.time()
        numsecs = currtime - start_time
        fps = frames / numsecs
        print "average FPS:", fps
