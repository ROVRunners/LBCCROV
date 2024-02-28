import cv2
import sys
import numpy as np

def nothing(x):
    pass

# Create a window
cv2.namedWindow('image')

# create trackbars for color change
cv2.createTrackbar('HMin','image',0,179,nothing) # Hue is from 0-179 for Opencv
cv2.createTrackbar('SMin','image',0,255,nothing)
cv2.createTrackbar('VMin','image',0,255,nothing)
cv2.createTrackbar('HMax','image',0,179,nothing)
cv2.createTrackbar('SMax','image',0,255,nothing)
cv2.createTrackbar('VMax','image',0,255,nothing)

# create trackbars for threshold
cv2.createTrackbar('TMin','image',0,255,nothing)
cv2.createTrackbar('TMax','image',0,255,nothing)

# Set default value for MAX HSV trackbars.
cv2.setTrackbarPos('HMax', 'image', 179)
cv2.setTrackbarPos('SMax', 'image', 255)
cv2.setTrackbarPos('VMax', 'image', 255)
cv2.setTrackbarPos('TMax', 'image', 255)

# Initialize to check if HSV min/max value changes
hMin = sMin = vMin = hMax = sMax = vMax = 0
phMin = psMin = pvMin = phMax = psMax = pvMax = 0

tMax = tMin = 0
ptMax = ptMin = 0

cap = cv2.VideoCapture(0)

#img = cv2.imread('1.png')
waitTime = 33

while(1):
    _, img = cap.read()
    output = img
#(hMin = 0 , sMin = 160, vMin = 51), (hMax = 24 , sMax = 255, vMax = 255)

    # get current positions of all trackbars
    hMin = cv2.getTrackbarPos('HMin','image')
    sMin = cv2.getTrackbarPos('SMin','image')
    vMin = cv2.getTrackbarPos('VMin','image')

    hMax = cv2.getTrackbarPos('HMax','image')
    sMax = cv2.getTrackbarPos('SMax','image')
    vMax = cv2.getTrackbarPos('VMax','image')

    tMin = cv2.getTrackbarPos('TMin','image')
    tMax = cv2.getTrackbarPos('TMax','image')

    # Set minimum and max HSV values to display
    lower = np.array([hMin, sMin, vMin])
    upper = np.array([hMax, sMax, vMax])

    # Create HSV Image and threshold into a range.
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    output = cv2.bitwise_and(img,img, mask= mask)

    grayscale = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
    _, filtered = cv2.threshold(grayscale, tMin, tMax, 0)

    # Print if there is a change in HSV value
    if((ptMax != tMax) | (ptMin != tMin) | (phMin != hMin) | (psMin != sMin) | (pvMin != vMin) | (phMax != hMax) | (psMax != sMax) | (pvMax != vMax) ):
        print("tMin=%d\ntMax=%d\nhMin = %d\nsMin = %d\nvMin = %d\nhMax = %d\nsMax = %d\nvMax = %d\n\n" % (tMin, tMax, hMin , sMin , vMin, hMax, sMax , vMax))
        phMin = hMin
        psMin = sMin
        pvMin = vMin
        phMax = hMax
        psMax = sMax
        pvMax = vMax
        ptMax = tMax
        ptMin = tMin

    # Display output image
    cv2.imshow('image',output)
    cv2.imshow('filtered',filtered)

    # Wait longer to prevent freeze for videos.
    if cv2.waitKey(waitTime) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
