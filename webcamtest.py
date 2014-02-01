

import cv2

webcam = cv2.VideoCapture()
cv2.namedWindow('preview')


if webcam.isOpened(): # try to get first frame
    rval, frame = webcam.read()
else:
    rval = False


while rval:
    cv2.imshow('preview', frame)

    rval, frame = webcam.read()

    key = cv2.waitKey(20);
    if key in [27, ord('Q'), ord('q')]: # exit on ESC or Q
        break
    
