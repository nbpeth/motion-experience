# http://docs.opencv.org/4.13.0/dd/d43/tutorial_py_video_display.html
# https://pypi.org/project/PyAutoGUI/

import pyautogui
import numpy as np
import cv2 as cv
 
cap = cv.VideoCapture(0)
backSub = cv.createBackgroundSubtractorMOG2()


if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
 
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    # Our operations on the frame come here
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    
    
    screenWidth, screenHeight = pyautogui.size() # Returns two integers, the width and height of the screen. (The primary monitor, in multi-monitor setups.)
    currentMouseX, currentMouseY = pyautogui.position() # Returns two integers, the x and y of the mouse cursor's current position.
    # print(screenWidth, screenHeight, currentMouseX, currentMouseY)
    # pyautogui.moveTo(-1556, 563)

    # Display the resulting frame
    # cv.imshow('frame', gray)
    # if cv.waitKey(1) == ord('q'):
    #     break
    # src_gray = cv.cvtColor(cv.imread, cv.COLOR_BGR2GRAY)
    fgMask = backSub.apply(gray)
    contours, hierarchy = cv.findContours(fgMask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # print(contours)
    if len(contours) > 0:
        largest = max(contours, key=cv.contourArea)
        m = cv.moments(largest)
        # print("?", m)
        if m['m00'] != 0:
            cx = int(m['m10'] / m['m00'])
            cy = int(m['m01'] / m['m00'])
            print(cx, cy)
            pyautogui.moveTo(cx, cy)
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()