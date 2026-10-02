from __future__ import annotations

from dataclasses import dataclass

import pytest

from vehicle.actions import VehicleActions
from vehicle.client import VehicleClient
from vehicle.telemetry import TelemetryMonitor


@dataclass(frozen=True)
class VehicleDependencies:
    telemetry: TelemetryMonitor
    actions: VehicleActions


@pytest.fixture
def vehicle_dependencies() -> VehicleDependencies:
    client = VehicleClient()
    client.connect()
    drone = client.get_drone()

    return VehicleDependencies(
        telemetry=TelemetryMonitor(drone),
        actions=VehicleActions(drone),
    )
