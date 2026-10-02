from __future__ import annotations

from tests.takeoff_test import TakeoffTest
from vehicle.actions import VehicleActions
from vehicle.client import VehicleClient
from vehicle.telemetry import TelemetryMonitor


def main() -> None:
    client = VehicleClient()
    client.connect()
    drone = client.get_drone()

    telemetry = TelemetryMonitor(drone)
    actions = VehicleActions(drone)

    TakeoffTest(
        telemetry,
        actions,
        target_altitude_m=2.0,
        timeout_s=10.0,
    ).run()


if __name__ == "__main__":
    main()
