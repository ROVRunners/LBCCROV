"""Created mostly by AI, no clue if it works, rewrite later."""

# pylint: disable=import-error

import time
import smbus2

# Initialize I2C bus.
bus = smbus2.SMBus(1)

# Sensor addresses:
PRESSURE_SENSOR_ADDRESS = 0x28
GYRO_ACCEL_ADDRESS = 0x68
MAGNETOMETER_ADDRESS = 0x1E


def read_pressure_sensor():
    """Read the pressure sensor data from the specified address.

    Returns:
        int: The pressure sensor data.
    """

    data = bus.read_i2c_block_data(PRESSURE_SENSOR_ADDRESS, 0x00, 4)
    pressure = (data[0] << 24) | (data[1] << 16) | (data[2] << 8) | data[3]
    return pressure


def read_gyro_accel() -> list[list[int]]:
    """Read the gyroscope and accelerometer data from the specified address.

    Returns:
        A list of lists containing the gyroscope and accelerometer data.\n
            The first list contains the gyroscope data [gyro_x, gyro_y, gyro_z].\n
            The second list contains the accelerometer data [accel_x, accel_y, accel_z].
    """

    bus.write_byte_data(GYRO_ACCEL_ADDRESS, 0x6B, 0x00)  # Power on the device
    time.sleep(0.1)

    gyro_x = bus.read_byte_data(GYRO_ACCEL_ADDRESS, 0x43)
    gyro_y = bus.read_byte_data(GYRO_ACCEL_ADDRESS, 0x45)
    gyro_z = bus.read_byte_data(GYRO_ACCEL_ADDRESS, 0x47)
    accel_x = bus.read_byte_data(GYRO_ACCEL_ADDRESS, 0x3B)
    accel_y = bus.read_byte_data(GYRO_ACCEL_ADDRESS, 0x3D)
    accel_z = bus.read_byte_data(GYRO_ACCEL_ADDRESS, 0x3F)

    return [[gyro_x, gyro_y, gyro_z], [accel_x, accel_y, accel_z]]


def read_magnetometer():
    """Read the magnetometer data from the specified address.

    Returns:
        A list containing the magnetometer data [magnetometer_x, magnetometer_y, magnetometer_z].
    """

    # Set continuous measurement mode
    bus.write_byte_data(MAGNETOMETER_ADDRESS, 0x02, 0x00)
    time.sleep(0.1)

    data = bus.read_i2c_block_data(MAGNETOMETER_ADDRESS, 0x03, 6)
    magnetometer_x = (data[0] << 8) | data[1]
    magnetometer_y = (data[2] << 8) | data[3]
    magnetometer_z = (data[4] << 8) | data[5]

    return [magnetometer_x, magnetometer_y, magnetometer_z]


def get_sensor_data() -> list[list]:
    """Get data from all sensors.

    Types are as follows: pressure, gyro, accel, magnetometer.

    Returns:
        list[list]: A list of sensor data in the format ["sensor type", data].
    """

    pressure_data = ["pressure", read_pressure_sensor()]
    gyro_data = ["gyro", read_gyro_accel()[0]]
    accel_data = ["accel", read_gyro_accel()[1]]
    magnetometer_data = ["magnetometer", read_magnetometer()]

    return [pressure_data, gyro_data, accel_data, magnetometer_data]
