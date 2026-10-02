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
