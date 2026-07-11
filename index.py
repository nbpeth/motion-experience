# http://docs.opencv.org/4.13.0/dd/d43/tutorial_py_video_display.html
# https://pypi.org/project/PyAutoGUI/

import pyautogui
import numpy as np
import cv2 as cv

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

CAMERA_INDEX = 0
MIN_CONTOUR_AREA = 3000
SMOOTHING = 0.3
MAX_STEP = 80

cap = cv.VideoCapture(CAMERA_INDEX)
backSub = cv.createBackgroundSubtractorMOG2()
screen_width, screen_height = pyautogui.size()

def largest_significant_contour(mask):
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    
    largest = max(contours, key=cv.contourArea)

    if cv.contourArea(largest) < MIN_CONTOUR_AREA:
        return None
    
    return largest

def contour_center_on_screen(contour, frame_w, frame_h):
    m = cv.moments(contour)
    if m['m00'] == 0:
        return None
    cx = m['m10'] / m['m00'] / frame_w * screen_width
    cy = m['m01'] / m['m00'] / frame_h * screen_height

    return cx, cy

def clamp(value, limit):
    return max(-limit, min(limit, value))

def update_cursor_from_motion(mask, frame_w, frame_h, smooth_x, smooth_y):
    contour = largest_significant_contour(mask)
    if contour is None:
        return smooth_x, smooth_y
    
    center = contour_center_on_screen(contour, frame_w, frame_h)
    if center is None:
        return smooth_x, smooth_y
    target_x, target_y = center
    smooth_x += clamp((target_x - smooth_x) * SMOOTHING, MAX_STEP)
    smooth_y += clamp((target_y - smooth_y) * SMOOTHING, MAX_STEP)
    pyautogui.moveTo(smooth_x, smooth_y)

    return smooth_x, smooth_y

def show_background_subtraction_mask(mask):
    cv.imshow('mask', mask)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

smooth_x, smooth_y = pyautogui.position()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame. Exiting")
        break

    frame = cv.flip(frame, 1)
    frame_h, frame_w = frame.shape[:2]

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    gray = cv.GaussianBlur(gray, (21, 21), 0)

    mask = backSub.apply(gray)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, np.ones((5, 5), np.uint8))

    show_background_subtraction_mask(mask)

    if cv.waitKey(1) == ord('q'):
        break

    smooth_x, smooth_y = update_cursor_from_motion(mask, frame_w, frame_h, smooth_x, smooth_y)

cap.release()
cv.destroyAllWindows()
