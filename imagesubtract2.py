import cv2
import cv2.cv as cv
import time
import RPi.GPIO as GPIO

GPIO.cleanup()

cv2.namedWindow('a', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('b', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('c', cv2.WINDOW_AUTOSIZE)

cap = cv2.VideoCapture(0)

cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv.CV_CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv.CV_CAP_PROP_EXPOSURE, 430)
cap.set(cv.CV_CAP_PROP_FPS, 30)

frames = 0

start_time = time.time()

#change numbers when we have LEDs to test with
#this sets up the LEDs on the GPIO
GPIO.setmode(GPIO.BOARD)
#GPIO.setup(11, GPIO.OUT)
#GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)

while True:
    #this turns the LEDs on
    #GPIO.output(11, True)
    #GPIO.output(13, True)
    GPIO.output(15, True)
    time.sleep(1)

    #print "fps = ", cap.get(cv.CV_CAP_PROP_FPS)
    #print "saturation = ", cap.get(cv.CV_CAP_PROP_SATURATION)
    #print "exposure = ", cap.get(cv.CV_CAP_PROP_EXPOSURE)
    retval, frame1 = cap.read()
    
    #this turns the LEDs off
    #GPIO.output(11, False)
    #GPIO.output(13, False)
    GPIO.output(15, False)
    time.sleep(1)

    #print "fps = ", cap.get(cv.CV_CAP_PROP_FPS)
    #print "saturation = ", cap.get(cv.CV_CAP_PROP_SATURATION)
    #print "exposure = ", cap.get(cv.CV_CAP_PROP_EXPOSURE)
    retval, frame2 = cap.read()

    #this converts the images to greyscale
    grey1 = cv2.cvtColor(frame1, cv.CV_RGB2GRAY)
    grey2 = cv2.cvtColor(frame2, cv.CV_RGB2GRAY)

    #this blurs the images
    blur1 = cv2.blur(grey1, (5, 5))
    blur2 = cv2.blur(grey2, (5, 5))

    #this takes the difference of the two images
    diff = cv2.absdiff(blur1, blur2)

    #this converts the image to black and white (threshold)
    #bw = cv2.adaptiveThreshold(diff, 50, cv.CV_ADAPTIVE_THRESH_GAUSSIAN_C, cv.CV_THRESH_BINARY, 5, 0)

    cv2.imshow('a', blur1)
    cv2.imshow('b', blur2)
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
