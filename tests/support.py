from __future__ import annotations

from dataclasses import dataclass

from vehicle.actions import VehicleActions
from vehicle.telemetry import TelemetryMonitor


@dataclass(frozen=True)
class VehicleDependencies:
    telemetry: TelemetryMonitor
    actions: VehicleActions
