from __future__ import annotations

from vehicle.vehicle import Vehicle


def test_takeoff_uses_configured_altitude(vehicle: Vehicle) -> None:
    vehicle.wait_until_ready_for_flight()

    with vehicle.parameters.temporary_value("MIS_TAKEOFF_ALT", 4.0):
        vehicle.arm()
        vehicle.take_off()
        vehicle.verify_altitude_is_above(3.5)
