from __future__ import annotations

from collections.abc import Iterator

import pytest

from vehicle.actions import VehicleActions
from vehicle.client import VehicleClient
from vehicle.telemetry import TelemetryMonitor
from vehicle.vehicle import Vehicle


@pytest.fixture
def vehicle() -> Iterator[Vehicle]:
    client = VehicleClient()
    client.connect()
    drone = client.get_drone()

    telemetry = TelemetryMonitor(drone)
    actions = VehicleActions(drone)
    connected_vehicle = Vehicle(actions, telemetry)

    telemetry.start()
    try:
        yield connected_vehicle
    finally:
        try:
            connected_vehicle.recover_to_safe_state()
        except Exception as recovery_error:
            print(f"Warn: failed to recover vehicle to safe state: {recovery_error}")
        telemetry.stop()
