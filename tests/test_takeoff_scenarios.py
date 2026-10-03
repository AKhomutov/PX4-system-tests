from __future__ import annotations

from vehicle.vehicle import Vehicle


def test_takeoff_reaches_expected_altitude(vehicle: Vehicle) -> None:
    vehicle.wait_until_ready_for_flight()
    vehicle.arm()
    vehicle.take_off()
    vehicle.verify_altitude_is_above(2.0)
