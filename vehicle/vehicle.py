from __future__ import annotations

from utils.wait import wait_until
from vehicle.actions import VehicleActions
from vehicle.telemetry import TelemetryMonitor


class Vehicle:
    def __init__(
        self,
        actions: VehicleActions,
        telemetry: TelemetryMonitor,
    ) -> None:
        self._actions = actions
        self._telemetry = telemetry

    def arm(self) -> None:
        self._actions.arm()

    def take_off(self) -> None:
        self._actions.takeoff()

    def land(self) -> None:
        self._actions.land()

    def disarm(self) -> None:
        self._actions.disarm()

    def is_on_ground(self) -> bool:
        return self._telemetry.is_on_ground()

    def is_armed(self) -> bool:
        return self._telemetry.is_armed()

    def has_position(self) -> bool:
        return self._telemetry.has_position()

    def wait_for_position(self, timeout_s: float = 10.0) -> None:
        wait_until(
            self.has_position,
            timeout_s,
            "first position telemetry",
        )

    def verify_altitude_is_above(
        self,
        altitude_m: float,
        timeout_s: float = 10.0,
    ) -> None:
        try:
            wait_until(
                lambda: self._telemetry.get_max_relative_altitude_m() > altitude_m,
                timeout_s,
                f"altitude > {altitude_m} m",
            )
        except TimeoutError as e:
            max_altitude_m = self._telemetry.get_max_relative_altitude_m()
            raise AssertionError(
                f"Altitude {altitude_m} m was not reached "
                f"within {timeout_s}s "
                f"(max relative_altitude_m: {max_altitude_m})"
            ) from e

    def verify_is_on_ground(self, timeout_s: float = 30.0) -> None:
        try:
            wait_until(self.is_on_ground, timeout_s, "landing (ON_GROUND)")
        except TimeoutError as e:
            raise AssertionError(
                f"Vehicle did not reach ON_GROUND within {timeout_s}s"
            ) from e

    def verify_is_disarmed(self, timeout_s: float = 10.0) -> None:
        try:
            wait_until(lambda: not self.is_armed(), timeout_s, "disarmed")
        except TimeoutError as e:
            raise AssertionError(
                f"Vehicle remained armed for more than {timeout_s}s"
            ) from e

    def recover_to_safe_state(
        self,
        *,
        landing_timeout_s: float = 30.0,
        disarm_timeout_s: float = 10.0,
    ) -> None:
        if self.is_on_ground():
            if self.is_armed():
                self.disarm()
                wait_until(
                    lambda: not self.is_armed(),
                    disarm_timeout_s,
                    "disarm during recovery",
                )
            return

        self.land()
        wait_until(
            self.is_on_ground,
            landing_timeout_s,
            "landing during recovery",
        )

        if self.is_armed():
            self.disarm()
            wait_until(
                lambda: not self.is_armed(),
                disarm_timeout_s,
                "disarm during recovery",
            )
