from __future__ import annotations

import pytest

from tests.support import VehicleDependencies
from vehicle.actions import VehicleActions
from vehicle.client import VehicleClient
from vehicle.telemetry import TelemetryMonitor


@pytest.fixture
def vehicle_dependencies() -> VehicleDependencies:
    client = VehicleClient()
    client.connect()
    drone = client.get_drone()

    return VehicleDependencies(
        telemetry=TelemetryMonitor(drone),
        actions=VehicleActions(drone),
    )
