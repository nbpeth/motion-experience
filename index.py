# http://docs.opencv.org/4.13.0/dd/d43/tutorial_py_video_display.html
# https://pypi.org/project/PyAutoGUI/

import pyautogui
import numpy as np
import cv2 as cv
 
cap = cv.VideoCapture(0)
backSub = cv.createBackgroundSubtractorMOG2()

def find_center_coordinates_of_contour(m):
    if m['m00'] != 0:
            cx = int(m['m10'] / m['m00'])
            cy = int(m['m01'] / m['m00'])
            # print(cx, cy)
    return cx, cy

def move_mouse_to_coordinates(cx, cy):
    pyautogui.moveTo(cx, cy)

def track_mouse_with_contour_center(m):
    cx, cy = find_center_coordinates_of_contour(m)
    move_mouse_to_coordinates(cx, cy)

def show_background_subtraction_mask(backSub, cv):
    bg = backSub.getBackgroundImage()
    if bg is not None and bg.size > 0:
        cv.imshow('background', bg)

if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    ret, frame = cap.read()
 
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    frame = cv.flip(frame, 1)
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    
    
    screenWidth, screenHeight = pyautogui.size() 
    currentMouseX, currentMouseY = pyautogui.position() 

    fgMask = backSub.apply(gray)

    # show_background_subtraction_mask(backSub, cv)

    if cv.waitKey(1) == ord('q'):
        break

    contours, hierarchy = cv.findContours(fgMask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    
    if len(contours) > 0:
        largest = max(contours, key=cv.contourArea)
        m = cv.moments(largest)
        
        track_mouse_with_contour_center(m)

cap.release()
cv.destroyAllWindows()