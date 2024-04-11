"""
"""
import os
from time import sleep
import socket
import serial
import CustomArduSubReplacement.JankTempSetupBypassingPixhawkWithArduino.Surface_Python.input_handler as input_handler

# Set the serial port names for your Arduino.
PORT = 'COM3' # Replace with the correct port for the Arduino.

# Initialize serial communication.
ARDUINO = serial.Serial(PORT, 19200, timeout=.02)

# Set the IP address and port for the PC and Pi. TODO: Change these to the correct values.
RPI_IP = '192.168.1.101'
RPI_PORT = 5601

# Set up the socket object to listen for connections.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((RPI_IP, RPI_PORT))
sock.listen(1)

# Accept a connection from the PC
print("Waiting for connection...")
connection, address = sock.accept()
print("Connected to PC:", address)


def receive_pwm_values():
    """Receive PWM values from the PC.

    Returns:
        list: A list of integers representing the received PWM values.
    """
    # Receive the PWM values from the PC.
    data = connection.recv(1024).decode()
    pwm_values = data.split()

    # Convert the PWM values to integers.
    pwm_values = [int(value) for value in pwm_values]

    return pwm_values


def process_data(data: str) -> list[str]:
    """Process the received data.

    Args:
        data (str): The data to process.

    Returns:
        str: The response to send back to the PC.
    """
    response = []

    if data.startswith('/'):
        command = data[1:]

        # Execute the command on the terminal.
        response[0] = os.system(command)

        # Error handling.
        if response[0] == 0:
            response[0] = "Command executed successfully."
        else:
            response[0] = "Error! Code: " + str(response[0])

    else:
        # Convert the data to PWM ints.
        pwm_values = data.split()

        pwm_values = [int(value) for value in pwm_values]

        # Send the PWM values to the Arduino.
        arduino_command = ' '.join(str(value) for value in pwm_values).encode()
        ARDUINO.write(arduino_command)

        print(arduino_command)

        # Prepare the response (e.g., sensor readings).
        response[0] = "Motors set to: " + arduino_command.decode()

    return response


def main():
    """The main function of the program."""
    # Read the data from the Arduino
    arduino_data = ARDUINO.readline()[0:-2]
    print("Read: ", arduino_data)

    # Receive and process data from the PC
    data = connection.recv(1024).decode()
    print("Received: ", data)

    response = process_data(data)

    # Send the response back to the PC
    send_data_to_pc(response)

    sleep(0.01)


def send_data_to_pc(data):
    """Send data to the PC.

    Args:
        data (str): The data to send.
    """
    connection.send(data.encode())
    print("Sending: " + data)


# def main():
#     """The main function of the program."""
#     # Read the data from the Arduino
#     arduino_data = ARDUINO.readline()[0:-2]
#     print("Read: ", arduino_data)

#     pwm_values = receive_pwm_values()
#     arduino_command = ' '.join(str(value) for value in pwm_values).encode()
#     ARDUINO.write(arduino_command)

#     print(arduino_command)

#     # Add a delay to control the update rate (adjust as needed)
#     time.sleep(0.01)


if __name__ == '__main__':
    try:
        while True:
            main()

    except KeyboardInterrupt:
        print("Program terminated by user.")
        ARDUINO.close()
        connection.close()
        sock.close()
