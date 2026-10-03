from __future__ import annotations

import time

from mavsdk.plugins.failure import FailureType

from utils.wait import wait_until
from vehicle.mission_builder import MissionBuilder
from vehicle.vehicle import Vehicle

ALTITUDE_CORRIDOR_TOLERANCE_M = 2.0
MISSION_TIMEOUT_S = 90.0
POLL_INTERVAL_S = 0.1


def assert_navigation_is_healthy(vehicle: Vehicle) -> None:
    assert vehicle.telemetry.is_armed()
    assert vehicle.telemetry.is_global_position_ok()
    assert vehicle.telemetry.is_local_position_ok()


def assert_altitude_within_mission_corridor(
    vehicle: Vehicle,
    expected_altitudes_m: list[float],
    tolerance_m: float,
) -> None:
    current_index = min(
        vehicle.mission.get_current_item_index(),
        len(expected_altitudes_m) - 1,
    )
    previous_index = max(current_index - 1, 0)

    previous_altitude_m = expected_altitudes_m[previous_index]
    target_altitude_m = expected_altitudes_m[current_index]
    lower_bound_m = min(previous_altitude_m, target_altitude_m) - tolerance_m
    upper_bound_m = max(previous_altitude_m, target_altitude_m) + tolerance_m

    altitude_m = vehicle.telemetry.get_relative_altitude_m()
    assert lower_bound_m <= altitude_m <= upper_bound_m, (
        f"Altitude {altitude_m:.2f} m is outside mission corridor "
        f"[{lower_bound_m:.2f}, {upper_bound_m:.2f}] m "
        f"(item {current_index}: {previous_altitude_m:.1f} -> {target_altitude_m:.1f})"
    )


def test_gps_failure_degrades_global_position_health(vehicle: Vehicle) -> None:
    vehicle.wait_for_position()
    assert vehicle.telemetry.is_global_position_ok()

    vehicle.failures.fail_gps(FailureType.OFF)

    wait_until(
        lambda: not vehicle.telemetry.is_global_position_ok(),
        timeout_s=10.0,
        description="global position to become unhealthy after GPS failure",
    )

    vehicle.failures.restore_gps()


def test_mission_remains_stable_after_barometer_failure(vehicle: Vehicle) -> None:
    vehicle.wait_for_position()

    latitude = vehicle.telemetry.get_latitude_deg()
    longitude = vehicle.telemetry.get_longitude_deg()

    mission_plan = (
        MissionBuilder()
        .add_waypoint(latitude + 0.00010, longitude, 5.0)
        .add_waypoint(latitude + 0.00010, longitude + 0.00010, 15.0)
        .add_waypoint(latitude, longitude + 0.00010, 8.0)
        .build()
    )
    expected_altitudes_m = [
        item.relative_altitude_m for item in mission_plan.mission_items
    ]

    vehicle.mission.upload(mission_plan)
    vehicle.arm()
    vehicle.mission.start()

    vehicle.verify_mission_progress_at_least(1 / 3)
    vehicle.failures.fail_barometer(FailureType.OFF)

    deadline = time.monotonic() + MISSION_TIMEOUT_S
    while not vehicle.mission.is_finished():
        if time.monotonic() >= deadline:
            raise AssertionError(
                f"Mission was not finished within {MISSION_TIMEOUT_S}s "
                "after barometer failure "
                f"(progress: {vehicle.mission.get_progress_fraction():.2f})"
            )

        assert_navigation_is_healthy(vehicle)
        assert_altitude_within_mission_corridor(
            vehicle,
            expected_altitudes_m,
            ALTITUDE_CORRIDOR_TOLERANCE_M,
        )

        time.sleep(POLL_INTERVAL_S)

    assert_navigation_is_healthy(vehicle)
