from __future__ import annotations

from utils.wait import wait_until
from vehicle.actions import VehicleActions
from vehicle.telemetry import TelemetryMonitor


class TakeoffTest:
    def __init__(
        self,
        telemetry: TelemetryMonitor,
        actions: VehicleActions,
        *,
        target_altitude_m: float = 2.0,
        timeout_s: float = 10.0,
        telemetry_timeout_s: float = 10.0,
    ) -> None:
        self._telemetry = telemetry
        self._actions = actions
        self._target_altitude_m = target_altitude_m
        self._timeout_s = timeout_s
        self._telemetry_timeout_s = telemetry_timeout_s

    def run(self) -> None:
        try:
            self._telemetry.start()
            try:
                self._wait_for_telemetry()
                self._actions.arm()
                self._actions.takeoff()
                self._assert_takeoff_altitude()
                print("Pass")
            except Exception:
                try:
                    self._cleanup()
                except Exception as cleanup_error:
                    print(
                        "Warn: failed to reset drone state after land/disarm: "
                        f"{cleanup_error}"
                    )
                raise
            else:
                self._cleanup()
        finally:
            self._telemetry.stop()

    def _wait_for_telemetry(self) -> None:
        wait_until(
            self._telemetry.has_position,
            self._telemetry_timeout_s,
            "first position telemetry",
        )

    def _assert_takeoff_altitude(self) -> None:
        try:
            wait_until(
                lambda: (
                    self._telemetry.get_max_relative_altitude_m()
                    > self._target_altitude_m
                ),
                self._timeout_s,
                f"takeoff altitude > {self._target_altitude_m} m",
            )
        except TimeoutError as e:
            max_altitude_m = self._telemetry.get_max_relative_altitude_m()
            print(
                f"Fail: did not reach expected altitude {self._target_altitude_m} m "
                f"within {self._timeout_s}s "
                f"(max relative_altitude_m: {max_altitude_m})"
            )
            raise AssertionError(
                f"Takeoff altitude {self._target_altitude_m} m was not reached "
                f"within {self._timeout_s}s "
                f"(max relative_altitude_m: {max_altitude_m})"
            ) from e

    def _cleanup(self) -> None:
        if self._telemetry.is_on_ground():
            if self._telemetry.is_armed():
                self._actions.disarm()
                wait_until(lambda: not self._telemetry.is_armed(), 10.0, "disarm")
            return

        self._actions.land()
        wait_until(self._telemetry.is_on_ground, 30.0, "landing (ON_GROUND)")

        if self._telemetry.is_armed():
            self._actions.disarm()
            wait_until(lambda: not self._telemetry.is_armed(), 10.0, "disarm")
