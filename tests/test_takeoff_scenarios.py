from __future__ import annotations

import pytest

from vehicle.vehicle import Vehicle


def test_takeoff_reaches_expected_altitude(vehicle: Vehicle) -> None:
    vehicle.wait_until_ready_for_flight()
    vehicle.arm()
    vehicle.take_off()
    vehicle.verify_altitude_is_above(2.0)


def test_takeoff_fails_when_expected_altitude_is_too_high(vehicle: Vehicle) -> None:
    vehicle.wait_until_ready_for_flight()
    vehicle.arm()
    vehicle.take_off()

    with pytest.raises(AssertionError, match=r"Altitude 5\.0 m was not reached"):
        vehicle.verify_altitude_is_above(5.0)
