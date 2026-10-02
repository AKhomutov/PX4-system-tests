from __future__ import annotations

from mavsdk import System
from mavsdk.plugins.action import Action


class VehicleActions:
    def __init__(self, drone: System) -> None:
        self._action = Action(drone)

    def arm(self) -> None:
        self._action.arm()

    def takeoff(self) -> None:
        self._action.takeoff()

    def land(self) -> None:
        self._action.land()

    def disarm(self) -> None:
        self._action.disarm()

    def return_to_launch(self) -> None:
        self._action.return_to_launch()

    def set_takeoff_altitude(self, altitude_m: float) -> None:
        self._action.set_takeoff_altitude(altitude_m)

    def set_return_to_launch_altitude(self, altitude_m: float) -> None:
        self._action.set_return_to_launch_altitude(altitude_m)

    def set_current_speed(self, speed_m_s: float) -> None:
        self._action.set_current_speed(speed_m_s)

    def goto_location(
        self,
        latitude_deg: float,
        longitude_deg: float,
        absolute_altitude_m: float,
        yaw_deg: float,
    ) -> None:
        self._action.goto_location(
            latitude_deg,
            longitude_deg,
            absolute_altitude_m,
            yaw_deg,
        )
