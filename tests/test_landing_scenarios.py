from __future__ import annotations

from scenarios.landing import LandingTest
from tests.support import VehicleDependencies


def test_landing_reaches_ground_and_disarms(
    vehicle_dependencies: VehicleDependencies,
) -> None:
    LandingTest(
        vehicle_dependencies.telemetry,
        vehicle_dependencies.actions,
        target_altitude_m=2.0,
        takeoff_timeout_s=10.0,
        landing_timeout_s=30.0,
        disarm_timeout_s=10.0,
    ).run()
