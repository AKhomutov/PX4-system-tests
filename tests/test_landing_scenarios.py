from __future__ import annotations

from vehicle.vehicle import Vehicle


def test_landing_reaches_ground_and_disarms(vehicle: Vehicle) -> None:
    vehicle.wait_for_position()
    vehicle.arm()
    vehicle.take_off()
    vehicle.verify_altitude_is_above(2.0)
    vehicle.land()
    vehicle.verify_is_on_ground()
    vehicle.verify_is_disarmed()
