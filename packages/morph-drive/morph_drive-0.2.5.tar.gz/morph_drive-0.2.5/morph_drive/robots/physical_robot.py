import logging
from abc import abstractmethod
from time import sleep
from types import TracebackType
from typing import Any, List, Optional, Type

import gymnasium
import numpy as np
import serial

from . import RobotInterface


# TODO separate the serial communication logic into a separate class and inherit
class PhyRobot(RobotInterface):
    """
    Implementation of RobotInterface for a real serial-based robot.
    Uses the Robot class (serial communication) to control servos.
    """

    # Only as per required by Gym interface
    metadata = {"render_modes": ["human"], "render_fps": 30}

    observation_space: gymnasium.spaces.Space
    action_space: gymnasium.spaces.Space

    def __init__(
        self,
        robot_name: str = "SimRobot",
        observation_space: gymnasium.spaces.Space | None = None,
        action_space: gymnasium.spaces.Space | None = None,
        configs: dict[str, Any] | None = None,
    ):
        """
        Initialize the serial robot interface.
        """
        super().__init__()

        if configs is None:
            configs = {}

        self.port = str(configs.get("port", "/dev/ttyUSB0"))
        self.baud_rate = int(configs.get("baud_rate", 115200))
        self.debug = bool(configs.get("debug", False))
        self.timeout = float(configs.get("timeout", 1.0))
        self.logger = logging.getLogger(__name__)

        self.robot_name = robot_name

        if observation_space is None:
            raise ValueError("Observation space must be provided.")

        if action_space is None:
            raise ValueError("Action space must be provided.")

        self.observation_space = observation_space
        self.action_space = action_space

        # Communication specific settings
        self.ser: Optional[serial.Serial] = None
        self._connect()

        self.position: list[int] = []

        if configs.get("init_position"):
            init_position = configs.get("init_position")
            if isinstance(init_position, (list, tuple)):
                self.position = [int(v) for v in init_position]
            else:
                raise ValueError(
                    "Invalid type for 'init_position'. Expected list, or tuple."
                )
        else:
            if self.action_space and hasattr(self.action_space, "shape"):
                self.position = [0] * self.action_space.shape[0]  # type: ignore
            else:
                raise ValueError(
                    "Action space must be properly initialized with a valid shape."
                )

    def get_observation_space(self) -> gymnasium.spaces.Space:
        """
        Return the observation space defined by the simulation
        """
        return self.observation_space

    def get_action_space(self) -> gymnasium.spaces.Space:
        """
        Return the action space defined by the simulation
        """
        return self.action_space

    def get_observation(self):
        """
        Get the current observation from the robot's sensors.
        """
        # TODO handle cases where sensor_readings is None or malformed
        yaw_deg, pitch_deg, roll_deg = self.get_sensor_readings()  # type: ignore

        obs = np.array([yaw_deg, pitch_deg, roll_deg], dtype=np.float32)

        # Store the last observation
        self._last_obs = obs

        return obs

    def apply_action(self, action: Any) -> None:
        """
        Apply an action to the robot by adjusting servo angles.
        """
        actuator_values: List = self.set_action_values(action)  # type: ignore
        actuator_cmd = " ".join(str(v) for v in actuator_values)
        self.write(f"W {actuator_cmd}\n")
        attempts = 0
        max_attempts = 10
        while self._read_raw() == "OK" and attempts < max_attempts:
            sleep(0.1)
            attempts += 1
        if attempts >= max_attempts:
            self.logger.warning(
                "Exceeded maximum attempts while waiting for response to", actuator_cmd
            )

        self.render()

    def render(self) -> None:
        """
        Render the robot's current state.
        """
        # TODO implement a visualization method for the robot
        # print(f"[{self.robot_name}] Actuators: {self.get_actuator_values()}")
        pass

    def close(self) -> None:
        """
        Close the connection to the robot.
        """
        self._close()

    def reset(self, *, seed=None, options=None):
        """
        Reset the robot to its initial state.
        """
        actuator_values: List = self.reset_action_values()  # type: ignore
        actuator_cmd = " ".join(str(v) for v in actuator_values)
        self.write(f"W {actuator_cmd}\n")

        return self.get_observation(), {}

    # ------------------------------------

    @abstractmethod
    def get_actuator_values(self):
        """
        Helper function to read the current actuator values in servo angles
        """

    @abstractmethod
    def set_action_values(self, servo_angles):
        """
        Helper function to set the action values based on servo angles.
        """

    def reset_action_values(self):
        """
        Helper function to define the action values into expected position.
        Generates random values within the action space by default
        """
        return self.action_space.sample()

    @abstractmethod
    def get_sensor_readings(self):
        """
        Helper function to read the sensor values
        """

    def _connect(self, retries: int = 3, delay: float = 2) -> bool:
        """
        Attempt to connect to the serial port with retries.
        """
        for attempt in range(1, retries + 1):
            try:
                self.ser = serial.Serial(
                    self.port, self.baud_rate, timeout=self.timeout
                )
                if self.ser.is_open:
                    self.logger.info(
                        "Connected to %s at %d baud.", self.port, self.baud_rate
                    )
                    return True
            except serial.SerialException as e:
                self.logger.warning(
                    "Connection failed (port:%s, baud_rate:%d attempt:%d). Retrying...",
                    self.port,
                    self.baud_rate,
                    attempt,
                )
                self.logger.debug(str(e))
                sleep(delay)
        raise ConnectionError(
            f"Failed to connect to {self.port} after {retries} attempts."
        )

    def read(self) -> Optional[str]:
        """
        Read a line from the serial port.
        """
        reading = self._read_raw()
        if reading == "OK":
            reading = self._read_raw()
        self.logger.debug("Received: %s", reading)
        return reading

    def write(self, string: str) -> Optional[bool]:
        """
        Write a string to the serial port.
        """
        if not self._is_serial_open() or self.ser is None:
            return None
        try:
            self._flush_input()  # Flush the serial input buffer before writing
            self.ser.write(string.encode())
            sleep(0.1)
            self.logger.debug("<< %s", string)

            # return (
            #     self.ser.readline() == "OK"
            # )  # Read the response to ensure it's processed
            return True
        except serial.SerialException as e:
            self.logger.error("Error while writing", exc_info=e)
            return False

    def _flush_input(self) -> None:
        """
        Flush the serial input buffer.
        """
        if self._is_serial_open() and self.ser is not None:
            self.logger.debug("Flushing input buffer...")
            self.ser.reset_input_buffer()

    def _close(self) -> None:
        """
        Close the serial port.
        """
        if self._is_serial_open() and self.ser is not None:
            self.ser.close()
            self.logger.info("Connection closed.")

    def _read_raw(self) -> Optional[str]:
        """
        Read raw data from the serial port.
        """
        if not self._is_serial_open() or self.ser is None:
            return None
        try:
            return self.ser.readline().decode().strip()
        except serial.SerialException as e:
            self.logger.error("Read error", exc_info=e)
            return None

    def _wait_for_ready(self) -> None:
        """
        Wait until the robot is ready.
        """
        self._flush_input()
        if not self._is_serial_open() or self.ser is None:
            return
        while (_ := self.read()) != "READY":
            sleep(0.5)
        self._flush_input()

    def _is_serial_open(self) -> bool:
        """
        Check if the serial port is open.
        """
        if not self.ser or not self.ser.is_open:
            self.logger.error("Serial port is not open.")
            return False
        return True

    def __enter__(self):
        self._connect()
        self.reset()
        self._wait_for_ready()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.close()

    def __del__(self) -> None:
        self.close()
