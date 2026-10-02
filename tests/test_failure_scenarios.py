from __future__ import annotations

from mavsdk.plugins.failure import FailureType

from utils.wait import wait_until
from vehicle.vehicle import Vehicle


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
