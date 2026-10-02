from __future__ import annotations

import pytest

from scenarios.takeoff import TakeoffTest
from tests.support import VehicleDependencies


def test_takeoff_reaches_expected_altitude(
    vehicle_dependencies: VehicleDependencies,
) -> None:
    TakeoffTest(
        vehicle_dependencies.telemetry,
        vehicle_dependencies.actions,
        target_altitude_m=2.0,
        timeout_s=10.0,
    ).run()


def test_takeoff_fails_when_expected_altitude_is_too_high(
    vehicle_dependencies: VehicleDependencies,
) -> None:
    with pytest.raises(AssertionError, match=r"Takeoff altitude 5\.0 m was not reached"):
        TakeoffTest(
            vehicle_dependencies.telemetry,
            vehicle_dependencies.actions,
            target_altitude_m=5.0,
            timeout_s=10.0,
        ).run()
