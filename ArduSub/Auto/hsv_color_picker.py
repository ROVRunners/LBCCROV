"""
Allows for the easy calibration of camera HSV filters for AI vision.
Provided By Jackson Smith.
"""
import cv2
import numpy as np

def nothing(x):
    """Does absolutely nothing!

    Args:
        x (Object): Completely irrelevant and useless!
    """
    pass

# Create a window.
cv2.namedWindow('image')

# Create trackbars for color change.
cv2.createTrackbar('HMin','image',0,179,nothing) # Hue is from 0-179 for OpenCV.
cv2.createTrackbar('SMin','image',0,255,nothing)
cv2.createTrackbar('VMin','image',0,255,nothing)
cv2.createTrackbar('HMax','image',0,179,nothing)
cv2.createTrackbar('SMax','image',0,255,nothing)
cv2.createTrackbar('VMax','image',0,255,nothing)

# Create trackbars for threshold.
cv2.createTrackbar('TMin','image',0,255,nothing)
cv2.createTrackbar('TMax','image',0,255,nothing)

# Set default value for MAX HSV trackbars.
cv2.setTrackbarPos('HMax', 'image', 179)
cv2.setTrackbarPos('SMax', 'image', 255)
cv2.setTrackbarPos('VMax', 'image', 255)
cv2.setTrackbarPos('TMax', 'image', 255)

# Initialize to check if HSV min/max value changes.
h_min = s_min = v_min = h_max = s_max = v_max = 0
ph_min = ps_min = pv_min = ph_max = ps_max = pv_max = 0

t_max = t_min = 0
pt_max = pt_min = 0

cap = cv2.VideoCapture(0)

#img = cv2.imread('1.png')
wait_time = 33

while(1):
    _, img = cap.read()
    output = img
    #(hMin = 0 , sMin = 160, vMin = 51), (hMax = 24 , sMax = 255, vMax = 255)

    # Get current positions of all trackbars.
    h_min = cv2.getTrackbarPos('HMin','image')
    s_min = cv2.getTrackbarPos('SMin','image')
    v_min = cv2.getTrackbarPos('VMin','image')

    h_max = cv2.getTrackbarPos('HMax','image')
    s_max = cv2.getTrackbarPos('SMax','image')
    v_max = cv2.getTrackbarPos('VMax','image')

    t_min = cv2.getTrackbarPos('TMin','image')
    t_max = cv2.getTrackbarPos('TMax','image')

    # Set minimum and max HSV values to display.
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])

    # Create HSV Image and threshold into a range.
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    output = cv2.bitwise_and(img,img, mask= mask)

    grayscale = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
    _, filtered = cv2.threshold(grayscale, t_min, t_max, 0)

    # Print if there is a change in HSV value.
    if((pt_max != t_max) | (pt_min != t_min) | (ph_min != h_min) | (ps_min != s_min) |
       (pv_min != v_min) | (ph_max != h_max) | (ps_max != s_max) | (pv_max != v_max) ):
        print(f"tMin={t_min}\ntMax={t_max}\nhMin = {h_min}\nsMin = {s_min}\nvMin = {v_min}" +
              f"\nhMax = {h_max}\nsMax = {s_max}\nvMax = {v_max}\n\n")
        ph_min = h_min
        ps_min = s_min
        pv_min = v_min
        ph_max = h_max
        ps_max = s_max
        pv_max = v_max
        pt_max = t_max
        pt_min = t_min

    # Display output image.
    cv2.imshow('image',output)
    cv2.imshow('filtered',filtered)

    # Wait longer to prevent freeze for videos.
    if cv2.waitKey(wait_time) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
