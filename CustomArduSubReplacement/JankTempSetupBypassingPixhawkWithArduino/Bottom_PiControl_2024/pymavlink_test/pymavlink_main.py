import sys

import time

from pymavlink import mavutil

port = "com16"  # Change this to the port that the pi is connected
connection = mavutil.mavlink_connection(port)

connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (connection.target_system, connection.target_component))

command_types = ['ATTITUDE_TARGET', 'UNKNOWN_8', 'SERVO_OUTPUT_RAW', 'VIBRATION', 'ESTIMATOR_STATUS', 'PING', 'SYS_STATUS', 'ACTUATOR_CONTROL_TARGET', 'SCALED_IMU2', 'TIMESYNC', 'ATTITUDE', 'ATTITUDE_QUATERNION', 'EXTENDED_SYS_STATE', 'UNKNOWN_411', 'ALTITUDE', 'BATTERY_STATUS', 'VFR_HUD', 'SCALED_IMU', 'HIGHRES_IMU', 'SYSTEM_TIME', 'HEARTBEAT', 'ODOMETRY']

while 1:
    msg = connection.recv_match(blocking=True, type="SERVO_OUTPUT_RAW")
    print(msg, end=f"\n---------------------------------------------------------------------------------------------\n")

# if not msg:
#     print("No message received")
# if msg and msg.get_type() == "BAD_DATA":
#     if mavutil.all_printable(msg.data):
#         sys.stdout.write(msg.data)
#         sys.stdout.flush()
# else:
#     #Message is valid
#     # Use the attribute
#     print('Mode: %s' % msg.mode)

# Define command_long_encode message to send MAV_CMD_SET_MESSAGE_INTERVAL command
# param1: MAVLINK_MSG_ID_BATTERY_STATUS (message to stream)
# param2: 1000000 (Stream interval in microseconds)
# message = connection.mav.command_long_encode(
#         connection.target_system,  # Target system ID
#         connection.target_component,  # Target component ID
#         mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send
#         0,  # Confirmation
#         mavutil.mavlink.MAVLINK_MSG_ID_BATTERY_STATUS,  # param1: Message ID to be streamed
#         1000000, # param2: Interval in microseconds
#         0,       # param3 (unused)
#         0,       # param4 (unused)
#         0,       # param5 (unused)
#         0,       # param5 (unused)
#         0        # param6 (unused)
#         )
#
# print("Message to send: %s" % message)
#
# # Send the COMMAND_LONG
# connection.mav.send(message)
#
# print("Message sent")
#
# # Wait for a response (blocking) to the MAV_CMD_SET_MESSAGE_INTERVAL command and print result
# # response = None
# # while response == None:
# #     response = mav.recv_match(type='COMMAND_ACK', blocking=False)
# #     print("response: %s" % response)
# response = connection.recv_match(type='COMMAND_ACK', blocking=True)
# if response and response.command == mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL and response.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
#     print("Command accepted")
# else:
#     print("Command failed")
#
#
# def send_heartbeat():
#     """
#     Send a MAVLink heartbeat message.
#     """
#     connection.wait_heartbeat(blocking=False, timeout=5)
#     print("Heartbeat from system (system %u component %u)" % (connection.target_system, connection.target_component))
#
#
# def main():
#     try:
#         while True:
#             send_heartbeat()
#             time.sleep(1)  # Send heartbeat every second
#     except KeyboardInterrupt:
#         print("\nExiting gracefully...")
#
#
# if __name__ == "__main__":
#     main()
