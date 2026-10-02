from __future__ import annotations

from utils.wait import wait_until
from vehicle.actions import VehicleActions
from vehicle.telemetry import TelemetryMonitor


class LandingTest:
    def __init__(
        self,
        telemetry: TelemetryMonitor,
        actions: VehicleActions,
        *,
        target_altitude_m: float = 2.0,
        takeoff_timeout_s: float = 10.0,
        landing_timeout_s: float = 30.0,
        disarm_timeout_s: float = 10.0,
        telemetry_timeout_s: float = 10.0,
    ) -> None:
        self._telemetry = telemetry
        self._actions = actions
        self._target_altitude_m = target_altitude_m
        self._takeoff_timeout_s = takeoff_timeout_s
        self._landing_timeout_s = landing_timeout_s
        self._disarm_timeout_s = disarm_timeout_s
        self._telemetry_timeout_s = telemetry_timeout_s

    def run(self) -> None:
        try:
            self._telemetry.start()
            try:
                self._wait_for_telemetry()
                self._actions.arm()
                self._actions.takeoff()
                self._assert_takeoff_altitude()

                self._actions.land()
                self._assert_landed_on_ground()
                self._assert_disarmed_after_landing()

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
                self._takeoff_timeout_s,
                f"takeoff altitude > {self._target_altitude_m} m",
            )
        except TimeoutError as e:
            max_altitude_m = self._telemetry.get_max_relative_altitude_m()
            raise AssertionError(
                f"Takeoff altitude {self._target_altitude_m} m was not reached "
                f"within {self._takeoff_timeout_s}s "
                f"(max relative_altitude_m: {max_altitude_m})"
            ) from e

    def _assert_landed_on_ground(self) -> None:
        try:
            wait_until(
                self._telemetry.is_on_ground,
                self._landing_timeout_s,
                "landing (ON_GROUND)",
            )
        except TimeoutError as e:
            raise AssertionError(
                f"Vehicle did not reach ON_GROUND within {self._landing_timeout_s}s "
                f"after land()"
            ) from e

    def _assert_disarmed_after_landing(self) -> None:
        try:
            wait_until(
                lambda: not self._telemetry.is_armed(),
                self._disarm_timeout_s,
                "disarmed after landing",
            )
        except TimeoutError as e:
            raise AssertionError(
                f"Vehicle remained armed for more than {self._disarm_timeout_s}s "
                f"after landing on ground"
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
