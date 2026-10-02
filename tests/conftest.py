from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest

from vehicle.actions import VehicleActions
from vehicle.client import VehicleClient
from vehicle.parameters import VehicleParameters
from vehicle.telemetry import TelemetryMonitor
from vehicle.vehicle import Vehicle


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[Any]) -> Any:
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture
def vehicle(request: pytest.FixtureRequest) -> Iterator[Vehicle]:
    client = VehicleClient()
    client.connect()
    drone = client.get_drone()

    telemetry = TelemetryMonitor(drone)
    actions = VehicleActions(drone)
    parameters = VehicleParameters(drone)
    connected_vehicle = Vehicle(actions, telemetry, parameters)

    telemetry.start()
    recovery_error: Exception | None = None
    try:
        yield connected_vehicle
    finally:
        try:
            connected_vehicle.recover_to_safe_state()
        except Exception as error:
            recovery_error = error
            print(f"Warn: failed to recover vehicle to safe state: {error}")
        telemetry.stop()

        call_report = getattr(request.node, "rep_call", None)
        test_failed = call_report is not None and call_report.failed
        if recovery_error is not None and not test_failed:
            raise recovery_error
