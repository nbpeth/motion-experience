# http://docs.opencv.org/4.13.0/dd/d43/tutorial_py_video_display.html
# https://pypi.org/project/PyAutoGUI/

import pyautogui
import numpy as np
import cv2 as cv
from typing import Sequence
import heapq

from contour_stream import ContourStreamer

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

CAMERA_INDEX = 1
MIN_CONTOUR_AREA = 3000
SMOOTHING = 0.3
MAX_STEP = 80

cap = cv.VideoCapture(CAMERA_INDEX)
backSub = cv.createBackgroundSubtractorMOG2()
screen_width, screen_height = pyautogui.size()

contour_streamer = ContourStreamer(port=8001)
contour_streamer.start()

def get_contours(mask) -> Sequence[cv.typing.MatLike] | None:
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    return contours

def get_top_n_contours(mask, n) -> Sequence[cv.typing.MatLike] | None:
    contours = get_contours(mask)

    if not contours:
        return None
    

    ceiling = min(n, len(contours))

    return tuple(heapq.nlargest(ceiling, contours, key=cv.contourArea))
    

def contour_center_on_screen(contour, frame_w, frame_h):
    m = cv.moments(contour)
    if m['m00'] == 0:
        return None
    
    cx = m['m10'] / m['m00'] / frame_w * screen_width
    cy = m['m01'] / m['m00'] / frame_h * screen_height

    return cx, cy

def clamp(value, limit):
    return max(-limit, min(limit, value))

def update_cursor_from_motion(contour, frame_w, frame_h, smooth_x, smooth_y):
    center = contour_center_on_screen(contour, frame_w, frame_h)
    if center is None:
        return smooth_x, smooth_y
    target_x, target_y = center
    smooth_x += clamp((target_x - smooth_x) * SMOOTHING, MAX_STEP)
    smooth_y += clamp((target_y - smooth_y) * SMOOTHING, MAX_STEP)
    # pyautogui.moveTo(smooth_x, smooth_y)

    return smooth_x, smooth_y

def contour_shape(contour):
    epsilon = 0.008 * cv.arcLength(contour, True)
    approx = cv.approxPolyDP(contour, epsilon, True)
    points = approx.reshape(-1, 2).tolist()

    m = cv.moments(contour)
    centroid = None
    if m['m00'] != 0:
        centroid = [m['m10'] / m['m00'], m['m01'] / m['m00']]

    return {"points": points, "centroid": centroid}

def contours_payload(contours, frame_w, frame_h):
    shapes = [contour_shape(c) for c in contours]
    return {"w": frame_w, "h": frame_h, "contours": shapes}

def show_background_subtraction_mask(mask):
    cv.imshow('L*a*b*', mask)

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

    hsv = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    hsv = cv.GaussianBlur(hsv, (21, 21), 0)

    # hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    # lower_blue = np.array([110,50,50])
    # upper_blue = np.array([130,255,255])
    # mask = cv.inRange(hsv, lower_blue, upper_blue)
    # mask = cv.GaussianBlur(mask, (21, 21), 0)
    # res = cv.bitwise_and(frame,frame, mask= mask)
    
    mask = backSub.apply(hsv)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, np.ones((5, 5), np.uint8))
    
    if cv.waitKey(1) == ord('q'):
        break

    contours = get_top_n_contours(mask, 3) or ()
    contours = [c for c in contours if cv.contourArea(c) >= MIN_CONTOUR_AREA]

    contour_streamer.publish_contours(contours_payload(contours, frame_w, frame_h))

    if contours:
        largest = max(contours, key=cv.contourArea)
        smooth_x, smooth_y = update_cursor_from_motion(largest, frame_w, frame_h, smooth_x, smooth_y)

cap.release()
cv.destroyAllWindows()


