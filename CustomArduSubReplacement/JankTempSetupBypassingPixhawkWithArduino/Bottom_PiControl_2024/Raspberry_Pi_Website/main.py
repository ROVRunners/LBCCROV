import os
import logging
import socketserver
from threading import Condition
from http import server
import json
import cv2
import input_handler
import threading

# pylint: disable=invalid-name
# pylint: disable=broad-exception-caught

# Put the HTML content of the main page in a variable from another file.
try:
    with open("/assets/main.html", mode="r", encoding="UTF-8") as file:
        PAGE = "".join(file.readlines()[:])
except FileNotFoundError:
    with open("CustomArduSubReplacement/JankTempSetupBypassingPixhawkWithArduino/" +
                "Bottom_PiControl_2024/Raspberry_Pi_Website/assets/main.html",
                mode="r", encoding="UTF-8") as file:
        PAGE = "".join(file.readlines()[:])


class StreamingOutput(object):
    """Represents an object for streaming output.

    Attributes:
        frame: The current frame.
        condition: A condition object for synchronization.
    """

    def __init__(self) -> None:
        """Initialize the StreamingOutput object."""
        self.frame = None
        self.condition = Condition()

    def write(self, frame) -> None:
        """Writes the given frame to the object and notifies all waiting threads.

        Args:
            frame: The frame to be written.
        """
        with self.condition:
            self.frame = frame
            self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
    """Handles HTTP requests for streaming video and gamepad/command inputs.

    Attributes:
        None

    Methods:
        do_GET(): Handles GET requests.
        do_POST(): Handles POST requests.
    """

    def do_GET(self) -> None:
        """Handle GET requests received by the server.

        The method checks the path of the request and performs the corresponding actions.

        If the path is '/', it redirects to '/index.html'.
        If the path is '/index.html', it sends the HTML content of the page.
        If the path is '/stream.mjpg', it streams the video frames.
        If the path is '/status', it sends the status information in JSON format.
        If the path is not recognized, it sends a 404 error.
        """

        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()

        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)

        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header(
                'Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    if frame is not None:

                        # cv2.imshow('Frame', frame)
                        # cv2.waitKey(1)  # This line is necessary to display the image

                        self.wfile.write(b'--FRAME\r\n')
                        self.send_header('Content-Type', 'image/jpeg')
                        self.send_header('Content-Length', len(frame))
                        self.end_headers()
                        self.wfile.write(frame)
                        self.wfile.write(b'\r\n')
                    else:
                        print("Frame is None")
                        placeholder_image = open(
                            'assets/unavailable.jpg', 'rb').read()
                        self.wfile.write(b'--FRAME\r\n')
                        self.send_header('Content-Type', 'image/jpeg')
                        self.send_header('Content-Length', len(placeholder_image))
                        self.end_headers()
                        self.wfile.write(placeholder_image)
                        self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))

        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = input_handler.get_status()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        else:
            self.send_error(404)
            self.end_headers()

    def do_POST(self) -> None:
        """Handle POST requests received by the server.

        This method is called when a POST request is received by the server.
        It processes the request based on the path and performs the necessary actions.

        Supported paths:
        - '/gamepad': Processes the gamepad input and logs the received data.
        - '/command': Processes the command input, logs the command response,
                        and returns the console log.

        Returns:
        - For '/gamepad': Sends a response with status code 200.
        - For '/command': Sends a response with status code 200 and the console log as JSON.

        Raises:
        - For unsupported paths: Sends a response with status code 404.
        """

        if self.path == '/gamepad':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            # Process the gamepad input here
            gamepad_data = json.loads(post_data.decode('utf-8'))
            input_handler.process_gamepad_input(gamepad_data)
            # Example: Log the received gamepad data
            print(post_data)
            self.send_response(200)
            self.end_headers()

        elif self.path == '/command':
            # Decode the POST data.
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            command_data = json.loads(post_data.decode('utf-8'))
            command = command_data['command']

            # Run the command and get a response.
            command_response = input_handler.process_command_input(command)

            print(command_response)
            print(post_data)

            # Send the response to the client.
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            # Check if the file terminal_log.txt exists and create it if it doesn't.
            if not os.path.exists('terminal_log.txt'):
                open('terminal_log.txt', 'w', encoding="UTF-8").close()

            # Update the log file and send the new log to the client.
            with open('terminal_log.txt', 'a', encoding="UTF-8") as f:
                f.write(command_response + '\n')
            with open('terminal_log.txt', 'r', encoding="UTF-8") as f:
                console_log = "</br>".join(f.readlines()[:])

            response = {'output': console_log}

            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    """
    A custom HTTP server for streaming data.

    This class extends the `HTTPServer` class and mixes in the `ThreadingMixIn` class
    to enable concurrent handling of multiple requests using threads.

    Attributes:
        allow_reuse_address (bool): Whether to allow reusing the server's address.
        daemon_threads (bool): Whether to use daemon threads for handling requests.
    """
    allow_reuse_address = True
    daemon_threads = True


output = StreamingOutput()
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

try:
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    def camera_thread():
        while True:
            ret, frame = camera.read()
            if not ret:
                print("Not ret")
                break
            output.write(frame)
            try:
                output.condition.acquire()
                output.condition.notify_all()
                output.condition.release()
            except RuntimeError as e:
                print("Failed notify: ", e)

    # Create and start the camera thread
    camera_thread = threading.Thread(target=camera_thread)
    camera_thread.start()
    server.serve_forever()
finally:
    camera.release()
