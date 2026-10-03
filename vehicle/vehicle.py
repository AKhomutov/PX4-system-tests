from __future__ import annotations

from mavsdk.plugins.telemetry import FlightMode

from utils.wait import wait_until
from vehicle.actions import VehicleActions
from vehicle.failures import VehicleFailures
from vehicle.info import VehicleInfo
from vehicle.mission import VehicleMission
from vehicle.parameters import VehicleParameters
from vehicle.telemetry import TelemetryMonitor


class Vehicle:
    def __init__(
        self,
        actions: VehicleActions,
        telemetry: TelemetryMonitor,
        parameters: VehicleParameters,
        mission: VehicleMission,
        failures: VehicleFailures,
        info: VehicleInfo,
    ) -> None:
        self.actions = actions
        self.telemetry = telemetry
        self.parameters = parameters
        self.mission = mission
        self.failures = failures
        self.info = info

    def arm(self) -> None:
        self.actions.arm()

    def take_off(self) -> None:
        self.actions.takeoff()

    def land(self) -> None:
        self.actions.land()

    def disarm(self) -> None:
        self.actions.disarm()

    def wait_for_position(self, timeout_s: float = 10.0) -> None:
        wait_until(
            self._has_position,
            timeout_s,
            "first position telemetry",
        )

    def wait_until_ready_for_flight(self, timeout_s: float = 15.0) -> None:
        wait_until(
            lambda: (
                self.telemetry.has_position()
                and self.telemetry.is_local_position_ok()
                and self.telemetry.is_global_position_ok()
                and self.telemetry.is_home_position_ok()
                and self.telemetry.is_armable()
            ),
            timeout_s,
            "vehicle to become ready for flight",
        )

    def verify_altitude_is_above(
        self,
        altitude_m: float,
        timeout_s: float = 10.0,
    ) -> None:
        try:
            wait_until(
                lambda: self.telemetry.get_max_relative_altitude_m() > altitude_m,
                timeout_s,
                f"altitude > {altitude_m} m",
            )
        except TimeoutError as e:
            max_altitude_m = self.telemetry.get_max_relative_altitude_m()
            raise AssertionError(
                f"Altitude {altitude_m} m was not reached "
                f"within {timeout_s}s "
                f"(max relative_altitude_m: {max_altitude_m})"
            ) from e

    def verify_is_on_ground(self, timeout_s: float = 30.0) -> None:
        try:
            wait_until(self._is_on_ground, timeout_s, "landing (ON_GROUND)")
        except TimeoutError as e:
            raise AssertionError(
                f"Vehicle did not reach ON_GROUND within {timeout_s}s"
            ) from e

    def verify_is_disarmed(self, timeout_s: float = 10.0) -> None:
        try:
            wait_until(lambda: not self._is_armed(), timeout_s, "disarmed")
        except TimeoutError as e:
            raise AssertionError(
                f"Vehicle remained armed for more than {timeout_s}s"
            ) from e

    def verify_flight_mode(
        self,
        expected_mode: FlightMode,
        timeout_s: float = 5.0,
    ) -> None:
        try:
            wait_until(
                lambda: self.telemetry.get_flight_mode() == expected_mode,
                timeout_s,
                f"flight mode == {expected_mode.name}",
            )
        except TimeoutError as e:
            current_mode = self.telemetry.get_flight_mode()
            raise AssertionError(
                f"Expected flight mode {expected_mode.name}, "
                f"but current mode is {current_mode.name}"
            ) from e

    def wait_for_mission_finished(self, timeout_s: float = 60.0) -> None:
        wait_until(
            self.mission.is_finished,
            timeout_s,
            "mission finished",
        )

    def verify_mission_finished(self, timeout_s: float = 60.0) -> None:
        try:
            self.wait_for_mission_finished(timeout_s=timeout_s)
        except TimeoutError as e:
            raise AssertionError(
                f"Mission was not finished within {timeout_s}s "
                f"(progress: {self.mission.get_progress_fraction():.2f}, "
                f"item {self.mission.get_current_item_index()}/"
                f"{self.mission.get_total_items_count()})"
            ) from e

    def verify_mission_progress_at_least(
        self,
        expected_fraction: float,
        timeout_s: float = 30.0,
    ) -> None:
        if not 0.0 <= expected_fraction <= 1.0:
            raise ValueError("expected_fraction must be between 0.0 and 1.0")

        try:
            wait_until(
                lambda: self.mission.get_progress_fraction() >= expected_fraction,
                timeout_s,
                f"mission progress >= {expected_fraction:.2f}",
            )
        except TimeoutError as e:
            raise AssertionError(
                f"Mission progress did not reach {expected_fraction:.2f} "
                f"within {timeout_s}s "
                f"(current: {self.mission.get_progress_fraction():.2f})"
            ) from e

    def recover_to_safe_state(
        self,
        *,
        landing_timeout_s: float = 30.0,
        disarm_timeout_s: float = 10.0,
    ) -> None:
        if self.telemetry.is_on_ground():
            if self.telemetry.is_armed():
                self.disarm()
                wait_until(
                    lambda: not self.telemetry.is_armed(),
                    disarm_timeout_s,
                    "disarm during recovery",
                )
            return

        if self.telemetry.is_in_air():
            self.land()
            wait_until(
                self.telemetry.is_on_ground,
                landing_timeout_s,
                "landing during recovery",
            )

            if self.telemetry.is_armed():
                self.disarm()
                wait_until(
                    lambda: not self.telemetry.is_armed(),
                    disarm_timeout_s,
                    "disarm during recovery",
                )
            return

        if self.telemetry.is_armed():
            raise RuntimeError(
                "Cannot safely recover vehicle: landed state is unknown while armed"
            )

    def reset_test_state(self) -> None:
        errors: list[Exception] = []

        try:
            self.failures.restore_all()
        except Exception as error:
            errors.append(error)

        try:
            self.recover_to_safe_state()
        except Exception as error:
            errors.append(error)

        try:
            self.mission.clear()
        except Exception as error:
            errors.append(error)

        if len(errors) == 1:
            raise errors[0]
        if errors:
            raise ExceptionGroup("Failed to reset vehicle test state", errors)

    def _is_on_ground(self) -> bool:
        return self.telemetry.is_on_ground()

    def _is_armed(self) -> bool:
        return self.telemetry.is_armed()

    def _has_position(self) -> bool:
        return self.telemetry.has_position()
