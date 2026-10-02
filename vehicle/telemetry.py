from __future__ import annotations

from typing import Any, Protocol

from mavsdk import System
from mavsdk.plugins.telemetry import (
    FixType,
    FlightMode,
    Health,
    LandedState,
    Telemetry,
)


class PositionLike(Protocol):
    relative_altitude_m: float


class TelemetryMonitor:
    def __init__(self, drone: System) -> None:
        self._telemetry = Telemetry(drone)
        self._handle: Any | None = None
        self._max_relative_altitude_m: float | None = None

    def start(self) -> None:
        if self._handle is not None:
            raise RuntimeError("TelemetryMonitor is already started")

        self._max_relative_altitude_m = None
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

    def get_relative_altitude_m(self) -> float:
        return float(self._telemetry.position().relative_altitude_m)

    def get_absolute_altitude_m(self) -> float:
        return float(self._telemetry.position().absolute_altitude_m)

    def get_latitude_deg(self) -> float:
        return float(self._telemetry.position().latitude_deg)

    def get_longitude_deg(self) -> float:
        return float(self._telemetry.position().longitude_deg)

    def get_max_relative_altitude_m(self) -> float:
        if self._max_relative_altitude_m is None:
            raise RuntimeError("No position telemetry received from subscription")
        return self._max_relative_altitude_m

    def get_gps_fix_type(self) -> FixType:
        return FixType(self._telemetry.gps_info().fix_type)

    def get_satellites_count(self) -> int:
        return int(self._telemetry.gps_info().num_satellites)

    def get_health(self) -> Health:
        return self._telemetry.health()

    def get_battery_remaining_percent(self) -> float:
        return float(self._telemetry.battery().remaining_percent)

    def get_voltage_v(self) -> float:
        return float(self._telemetry.battery().voltage_v)

    def get_roll_deg(self) -> float:
        return float(self._telemetry.attitude_euler().roll_deg)

    def get_pitch_deg(self) -> float:
        return float(self._telemetry.attitude_euler().pitch_deg)

    def get_yaw_deg(self) -> float:
        return float(self._telemetry.attitude_euler().yaw_deg)

    def get_velocity_north_m_s(self) -> float:
        return float(self._telemetry.velocity_ned().north_m_s)

    def get_velocity_east_m_s(self) -> float:
        return float(self._telemetry.velocity_ned().east_m_s)

    def get_velocity_down_m_s(self) -> float:
        return float(self._telemetry.velocity_ned().down_m_s)

    def get_landed_state(self) -> LandedState:
        return LandedState(self._telemetry.landed_state())

    def get_flight_mode(self) -> FlightMode:
        return FlightMode(self._telemetry.flight_mode())

    def has_position(self) -> bool:
        return self._max_relative_altitude_m is not None

    def is_local_position_ok(self) -> bool:
        return bool(self.get_health().is_local_position_ok)

    def is_global_position_ok(self) -> bool:
        return bool(self.get_health().is_global_position_ok)

    def is_home_position_ok(self) -> bool:
        return bool(self.get_health().is_home_position_ok)

    def is_accelerometer_calibration_ok(self) -> bool:
        return bool(self.get_health().is_accelerometer_calibration_ok)

    def is_gyrometer_calibration_ok(self) -> bool:
        return bool(self.get_health().is_gyrometer_calibration_ok)

    def is_magnetometer_calibration_ok(self) -> bool:
        return bool(self.get_health().is_magnetometer_calibration_ok)

    def is_on_ground(self) -> bool:
        return bool(self.get_landed_state() == LandedState.ON_GROUND)

    def is_in_air(self) -> bool:
        return bool(self._telemetry.in_air())

    def is_armed(self) -> bool:
        return bool(self._telemetry.armed())

    def is_armable(self) -> bool:
        return bool(self.get_health().is_armable)
