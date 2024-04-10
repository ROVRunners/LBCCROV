import argparse
import os
from flask import Flask, render_template, Response, jsonify, request
import cv2
import input_handler
import threading
from imutils.video import VideoStream
import time

# pylint: disable=invalid-name

outputFrame = None
lock = threading.Lock()
app = Flask(__name__)
vs = VideoStream(src=0).start()

time.sleep(2.0)

# Put the HTML content of the main page in a variable from another file.
# try:
#     with open("assets/main.html", mode="r", encoding="UTF-8") as file:
#         PAGE = "".join(file.readlines()[:])
# except FileNotFoundError:
#     with open("CustomArduSubReplacement/JankTempSetupBypassingPixhawkWithArduino/" +
#               "Bottom_PiControl_2024/Raspberry_Pi_Website/assets/main.html",
#               mode="r", encoding="UTF-8") as file:
#         PAGE = "".join(file.readlines()[:])


def update_frame():
	# grab global references to the video stream, output frame, and
	# lock variables
	global vs, outputFrame, lock

    # loop over frames from the video stream
	while True:
		# read the next frame from the video stream, resize it,
		# convert the frame to grayscale, and blur it
		frame = vs.read()

		with lock:
			outputFrame = frame.copy()


def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock
	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue
			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
			# ensure the frame was successfully encoded
			if not flag:
				continue
		# yield the output frame in the byte format
		yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                    bytearray(encodedImage) + b'\r\n')


@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

# class StreamingOutput(object):
#     """Represents an object for streaming output.

#     Attributes:
#         frame: The current frame.
#         condition: A condition object for synchronization.
#     """

#     def __init__(self) -> None:
#         """Initialize the StreamingOutput object."""
#         self.frame = None
#         self.condition = threading.Condition()

#     def write(self, frame) -> None:
#         """Writes the given frame to the object and notifies all waiting threads.

#         Args:
#             frame: The frame to be written.
#         """
#         with self.condition:
#             self.frame = frame
#             self.condition.notify_all()


# output = StreamingOutput()
# camera = cv2.VideoCapture(0)
# camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


# def camera_thread():
#     while True:
#         ret, frame = camera.read()
#         if not ret:
#             print("Not ret")
#             break
#         output.write(frame)
#         try:
#             with output.condition:
#                 output.condition.notify_all()
#         except RuntimeError as e:
#             print("Failed notify: ", e)


@app.route('/')
def index():
    return render_template('index.html')


# @app.route('/stream.mjpg')
# def stream():
#     def generate():
#         while True:
#             with output.condition:
#                 output.condition.wait()
#                 frame = output.frame
#             if frame is not None:
#                 ret, jpeg = cv2.imencode('.jpg', frame)
#                 frame_bytes = jpeg.tobytes()
#                 yield (b'--FRAME\r\n'
#                        b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
#             else:
#                 print("Frame is None")
#                 placeholder_image = open('assets/unavailable.jpg', 'rb').read()
#                 yield (b'--FRAME\r\n'
#                        b'Content-Type: image/jpeg\r\n\r\n' + placeholder_image + b'\r\n\r\n')

#     return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=FRAME')


@app.route('/status')
def status():
    response = input_handler.get_status()
    return jsonify(response)


@app.route('/gamepad', methods=['POST'])
def gamepad():
    gamepad_data = request.get_json()
    input_handler.process_gamepad_input(gamepad_data)
    print(gamepad_data)
    return '', 200


@app.route('/command', methods=['POST'])
def command():
    command_data = request.get_json()
    command = command_data['command']
    command_response = input_handler.process_command_input(command)
    print(command_response)
    print(command_data)

    # Check if the file terminal_log.txt exists and create it if it doesn't.
    if not os.path.exists('terminal_log.txt'):
        open('terminal_log.txt', 'w', encoding="UTF-8").close()

    # Update the log file and send the new log to the client.
    with open('terminal_log.txt', 'a', encoding="UTF-8") as f:
        f.write(command_response + '\n')
    with open('terminal_log.txt', 'r', encoding="UTF-8") as f:
        console_log = "</br>".join(f.readlines()[:])

    response = {'output': console_log}

    return jsonify(response), 200


if __name__ == '__main__':
	# construct the argument parser and parse command line arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--ip", type=str, required=True,
                 	help="ip address of the device")
	ap.add_argument("-o", "--port", type=int, required=True,
                 	help="ephemeral port number of the server (1024 to 65535)")
	args = vars(ap.parse_args())
	t = threading.Thread(target=update_frame)
	t.daemon = True
	t.start()
	# start the flask app
	app.run(host=args["ip"], port=args["port"], debug=True,
            threaded=True, use_reloader=False)
# release the video stream pointer
vs.stop()

