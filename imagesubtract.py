import cv2.cv as cv
import time

cv.NamedWindow('a', 1)
cv.NamedWindow('b', 1)
cv.NamedWindow('c', 1)
cap = cv.CaptureFromCAM(-1)
cv.SetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_HEIGHT, 240)
cv.SetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_WIDTH, 320)

frames = 0
start_time = time.time()
while True:
    frame1 = cv.QueryFrame(cap)
    time.sleep(5)
    frame2 = cv.QueryFrame(cap)

    grey1 = cv.CreateImage(cv.GetSize(frame1), frame1.depth, 1)
    cv.CvtColor(frame1, grey1, cv.CV_RGB2GRAY)

    grey2 = cv.CreateImage(cv.GetSize(frame2), frame2.depth, 1)
    cv.CvtColor(frame2, grey2, cv.CV_RGB2GRAY)

    blur1 = cv.CreateImage(cv.GetSize(frame1), frame1.depth, 1)
    cv.Smooth(grey1, blur1, cv.CV_BLUR, 15, 15)

    blur2 = cv.CreateImage(cv.GetSize(frame1), frame1.depth, 1)
    cv.Smooth(grey2, blur2, cv.CV_BLUR, 15, 15)

    diff = cv.CreateImage(cv.GetSize(frame1), frame1.depth, 1)
    cv.AbsDiff(blur1, blur2, diff)
    
    cv.ShowImage('a', blur1)
    cv.ShowImage('b', blur2)
    cv.ShowImage('c', diff)

    #cv.SaveImage('frame1.png', frame1)
    #cv.SaveImage('frame2.png', frame2)

    #exit(0)
    
    c = cv.WaitKey(50)
    if c == 27:
        exit(0)

    print "Frame", frames
    frames += 1

    if frames % 10 == 0:
        currtime = time.time()
        numsecs = currtime - start_time
        fps = frames / numsecs
        print "average FPS:", fps
    
