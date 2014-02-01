import cv2.cv as cv
import time
 
cv.NamedWindow('a', 1)
cv.NamedWindow('b', 1)
cv.NamedWindow('c', 1)
cv.NamedWindow('d', 1)
cap = cv.CaptureFromCAM(-1)
cv.SetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_HEIGHT, 240)
cv.SetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_WIDTH, 320)
 
frames = 0
start_time = time.time()
while True:
  frame = cv.QueryFrame(cap)
  cv.ShowImage('a', frame)
 
  # Convert to greyscale
  grey = cv.CreateImage(cv.GetSize(frame), frame.depth, 1)
  cv.CvtColor(frame, grey, cv.CV_RGB2GRAY)
  cv.ShowImage('b', grey)
  
  # Gaussian blur to remove noise
  blur = cv.CreateImage(cv.GetSize(grey), cv.IPL_DEPTH_8U, grey.channels)
  cv.Smooth(grey, blur, cv.CV_GAUSSIAN, 5, 5)
  cv.ShowImage('c', blur)
 
  # And do Canny edge detection
  canny = cv.CreateImage(cv.GetSize(blur), blur.depth, blur.channels)
  cv.Canny(blur, canny, 10, 100, 3)
  cv.ShowImage('d', canny)
 
  c = cv.WaitKey(50)
  if c == 27:
    exit(0) 
  
  # Apparently not supported for my cameras:
  # print "FPS:", cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FPS)
 
  print "Frame", frames
  frames += 1
 
  if frames % 10 == 0:
    currtime = time.time()
    numsecs = currtime - start_time
    fps = frames / numsecs
    print "average FPS:", fps

