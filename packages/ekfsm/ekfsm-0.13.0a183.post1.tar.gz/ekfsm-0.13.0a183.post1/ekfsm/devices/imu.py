class ImuSample:
    """
    Class to store IMU data sample

    * accel: list[float] - Accelerometer data in m/s^2, [x, y, z]
    * gyro: list[float] - Gyroscope data in degrees/s, [x, y, z]
    * lost: bool - True if data was lost before that sample

    """

    def __init__(self, accel: list[float], gyro: list[float], lost: bool):
        self.accel = accel
        self.gyro = gyro
        self.lost = lost
