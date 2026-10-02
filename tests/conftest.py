from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest

from vehicle.actions import VehicleActions
from vehicle.client import VehicleClient
from vehicle.failures import VehicleFailures
from vehicle.mission import VehicleMission
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
    mission = VehicleMission(drone)
    failures = VehicleFailures(drone)
    connected_vehicle = Vehicle(actions, telemetry, parameters, mission, failures)

    telemetry.start()
    cleanup_errors: list[Exception] = []
    try:
        yield connected_vehicle
    finally:
        try:
            connected_vehicle.reset_test_state()
        except Exception as error:
            cleanup_errors.append(error)
            print(f"Warn: failed to reset vehicle test state: {error}")

        try:
            telemetry.stop()
        except Exception as error:
            cleanup_errors.append(error)
            print(f"Warn: failed to stop telemetry: {error}")

        call_report = getattr(request.node, "rep_call", None)
        test_failed = call_report is not None and call_report.failed
        if cleanup_errors and not test_failed:
            if len(cleanup_errors) == 1:
                raise cleanup_errors[0]
            raise ExceptionGroup(
                "Failed to clean up vehicle fixture",
                cleanup_errors,
            )
