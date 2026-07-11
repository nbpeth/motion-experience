import cv2 as cv

for index in range(6):
    cap = cv.VideoCapture(index)
    if not cap.isOpened():
        cap.release()
        print(f"index {index}: not available")
        continue
    ret, frame = cap.read()
    if ret and frame is not None:
        h, w = frame.shape[:2]
        brightness = frame.mean()
        note = "ALL BLACK" if brightness < 1 else f"mean brightness {brightness:.1f}"
        print(f"index {index}: OPEN  {w}x{h}  ({note})")
    else:
        print(f"index {index}: opened but returned no frame")
    cap.release()
