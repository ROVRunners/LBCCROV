import numpy as np
import cv2
from pymavlink import mavutil

cap = cv2.VideoCapture(0)

hMin = 0
sMin = 95
vMin = 143
hMax = 179
sMax = 255
vMax = 255


# Create the connection
master = mavutil.mavlink_connection('udp:172.21.96.1:14550')
# Wait a heartbeat before sending commands
master.wait_heartbeat()

# Create a function to send RC values
# More information about Joystick channels
# here: https://www.ardusub.com/operators-manual/rc-input-and-output.html#rc-inputs
def set_rc_channel_pwm(channel_id, pwm=0):
    # [-1,1] -> [1100,1900]
    pwm = int(400*pwm + 1500)
    
    """ Set RC channel pwm value
    Args:
        channel_id (TYPE): Channel ID
        pwm (int, optional): Channel pwm value 1100-1900
    """
    if channel_id < 1 or channel_id > 11:
        print("Channel does not exist.")
        return

    # Mavlink 2 supports up to 18 channels:
    # https://mavlink.io/en/messages/common.html#RC_CHANNELS_OVERRIDE
    rc_channel_values = [65535 for _ in range(11)]
    rc_channel_values[channel_id - 1] = pwm
    master.mav.rc_channels_override_send(
        master.target_system,                # target_system
        master.target_component,             # target_component
        *rc_channel_values)                  # RC channel list, in microseconds.

"""
1	Pitch
2	Roll
3	Throttle
4	Yaw
5	Forward
6	Lateral
7	Camera Pan
8	Camera Tilt*
9	Lights 1 Level
10	Lights 2 Level
11	Video Switch"""

FORWARD = 5
YAW = 4


def dilatation(src):
    dilatation_size = 10
    dilation_shape = cv2.MORPH_ELLIPSE
    element = cv2.getStructuringElement(dilation_shape, (2 * dilatation_size + 1, 2 * dilatation_size + 1),
                                       (dilatation_size, dilatation_size))
    dilatation_dst = cv2.dilate(src, element)
    return dilatation_dst
    


lower = np.array([hMin, sMin, vMin])
upper = np.array([hMax, sMax, vMax])

while 1:
    ret,img = cap.read()

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    output = cv2.bitwise_and(img,img, mask= mask)

    grayscale = cv2.cvtColor(output, cv2.COLOR_HSV2GRAY)

    dilatation(grayscale)
    ret, thresh = cv2.threshold(grayscale, 50, 255, 0)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        cnt = max(contours, key=cv2.contourArea)

        if cv2.contourArea(cnt) > 2000:
        
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.intp(box)
            cv2.drawContours(img, [box], 0, (0, 255, 0), 2)
            
            M = cv2.moments(cnt)

            center = (box[0]+box[2])//2
            img = cv2.circle(img, center, radius=5, color=(0,255,0), thickness=-1)

            if M['m00']:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                img = cv2.circle(img, (cx,cy), radius=5, color=(255,0,0), thickness=-1)

                error = cx - 320
                set_rc_channel_pwm(YAW, error/300)
                set_rc_channel_pwm(FORWARD,- (cy - 240)/150)
                    

            cv2.drawContours(img, [cnt], 0, (0,255,0), 3)
            
    cv2.imshow("G", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
