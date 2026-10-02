from __future__ import annotations

from vehicle.vehicle import Vehicle


def test_vehicle_information_is_available(vehicle: Vehicle) -> None:
    assert vehicle.info.get_hardware_uid()
    assert vehicle.info.get_product_name()
    assert vehicle.info.get_vendor_name()
    assert vehicle.info.get_flight_software_version()
    assert vehicle.info.get_flight_software_git_hash()

    assert vehicle.info.get_speed_factor() > 0.0
