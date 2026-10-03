from __future__ import annotations

from mavsdk.plugins.telemetry import FixType

from vehicle.vehicle import Vehicle


def test_vehicle_is_ready_for_flight(vehicle: Vehicle) -> None:
    vehicle.wait_until_ready_for_flight()

    assert vehicle.telemetry.is_accelerometer_calibration_ok()
    assert vehicle.telemetry.is_gyrometer_calibration_ok()
    assert vehicle.telemetry.is_magnetometer_calibration_ok()
    assert vehicle.telemetry.get_gps_fix_type() >= FixType.FIX_3D
    assert vehicle.telemetry.get_satellites_count() > 0
