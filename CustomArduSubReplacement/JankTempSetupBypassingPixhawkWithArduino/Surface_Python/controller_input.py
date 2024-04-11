import os
import pygame

from utilities.personal_functions import *


class Controller:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        if not pygame.joystick.get_count() == 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.get_controls()
        else:
            error("Warning! No controller detected!")

    def get_inputs(self) -> list:
        return inputs

    def get_button(self, button):
        return self.joystick.get_button(button)

    def get_joystick(self, axis):
        return self.joystick.get_axis(axis)

    def get_hat(self, hat):
        return self.joystick.get_hat(hat)


    def get_controls(self) -> dict:
        """Get the controls and map them to the keys in the file.

        Returns:
            dict: The controls and their keys.
        """
        self.name_numeral_button_map = {
            "A": 0,
            "B": 1,
            "X": 2,
            "Y": 3,
            "LEFT_BUMPER": 4,
            "RIGHT_BUMPER": 5,
            "SELECT": 6,
            "START": 7,
        }
        self.name_numeral_variable_map = {
            "LEFT_X": 0,
            "LEFT_Y": 1,
            "RIGHT_X": 2,
            "RIGHT_Y": 3,
            "LEFT_TRIGGER": 4,
            "RIGHT_TRIGGER": 5,
        }
        self.name_numeral_dpad_map = {
            "DPAD_LEFT": (-1, 0),
            "DPAD_RIGHT": (1, 0),
            "DPAD_UP": (0, 1),
            "DPAD_DOWN": (0, -1),
        }

        self.action_number_map = {
            # Lateral movement
            "FORWARD": None,
            "BACKWARD": None,
            "LEFT": None,
            "RIGHT": None,
            "UP": None,
            "DOWN": None,

            # Rotational movement
            "YAW_LEFT": None,
            "YAW_RIGHT": None,
            # "ROLL_LEFT": None,    Maybe add in future
            # "ROLL_RIGHT": None,
            "PITCH_UP": None,
            "PITCH_DOWN": None,
            
            # Other
            
        }

        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(path, "data")
        path = os.path.join(path, "default_controls.txt")

        file = open(path, "r", encoding="UTF-8")

        file_lines = file.readlines()[:]

        control_map = {}

        for line in file_lines:

            if line.startswith("#"):
                return control_map

            control = line.split("=")

            button = control[1].strip().lower()
            ctrl = control[0].strip().lower()

            if not ctrl in control_map:
                control_map[ctrl] = []

            control_map[ctrl].append(button)

        file.close()

        return control_map
