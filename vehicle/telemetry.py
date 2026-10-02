from __future__ import annotations

import time
from typing import Any, Protocol

from mavsdk import System
from mavsdk.plugins.telemetry import LandedState, Telemetry


class PositionLike(Protocol):
    absolute_altitude_m: float
    relative_altitude_m: float


class TelemetryMonitor:
    def __init__(self, drone: System) -> None:
        self._telemetry = Telemetry(drone)
        self._handle: Any | None = None
        self._last_print: float = 0.0
        self._max_relative_altitude_m: float | None = None

    def start(self) -> None:
        if self._handle is not None:
            raise RuntimeError("TelemetryMonitor is already started")

        self._max_relative_altitude_m = None
        self._last_print = 0.0
        self._handle = self._telemetry.subscribe_position(self._on_position)

    def stop(self) -> None:
        if self._handle is not None:
            self._telemetry.unsubscribe_position(self._handle)
            self._handle = None

    def _on_position(
        self,
        position: PositionLike,
        error: object | None,
    ) -> None:
        if (
            self._max_relative_altitude_m is None
            or position.relative_altitude_m > self._max_relative_altitude_m
        ):
            self._max_relative_altitude_m = position.relative_altitude_m

        now = time.monotonic()

        if now - self._last_print >= 0.5:
            print(
                position.absolute_altitude_m,
                position.relative_altitude_m,
                self._max_relative_altitude_m,
            )
            self._last_print = now

    def get_max_relative_altitude_m(self) -> float:
        if self._max_relative_altitude_m is None:
            raise RuntimeError("No position telemetry received from subscription")
        return self._max_relative_altitude_m

    def has_position(self) -> bool:
        return self._max_relative_altitude_m is not None

    def is_on_ground(self) -> bool:
        return bool(self._telemetry.landed_state() == LandedState.ON_GROUND)

    def is_armed(self) -> bool:
        return bool(self._telemetry.armed())
