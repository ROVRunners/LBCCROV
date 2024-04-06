"""Streams video from two USB cameras to the PC."""

# pylint: disable=no-member
# pylint: disable=invalid-name

import socket
import struct
import pickle
import cv2

PC_PORT = 5600

# Toggle to stop video streaming.
stream = True

def stream_video(pc_ip: str, quantity: int = 2) -> None:
    """Stream video from two USB cameras to the PC."""

    # Verify quantity is valid.
    if quantity < 1:
        raise ValueError("Quantity must be greater than 0.")

    # Set up the USB cameras and socket connection.
    camera_list = [cv2.VideoCapture(i) for i in range(quantity)]

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((pc_ip, PC_PORT))

    while stream:
        # Read frames from the cameras
        frame_list = [camera.read() for camera in camera_list]

        # Format the frames
        data = pickle.dumps((frame for frame in frame_list))
        message_size = struct.pack("L", len(data))

        # Send the message size to the PC
        client_socket.sendall(message_size)

        # Send the serialized frames to the PC
        client_socket.sendall(data)

    # Release the camera resources
    camera_list = [camera.release() for camera in camera_list]

    client_socket.close()
