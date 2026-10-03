from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from typing import Any

import pytest

from vehicle.actions import VehicleActions
from vehicle.client import CONNECTION_URL_ENV, DEFAULT_CONNECTION_URL, VehicleClient
from vehicle.failures import VehicleFailures
from vehicle.info import VehicleInfo
from vehicle.mission import VehicleMission
from vehicle.parameters import VehicleParameters
from vehicle.telemetry import TelemetryMonitor
from vehicle.vehicle import Vehicle

logger = logging.getLogger(__name__)


def get_connection_url(request: pytest.FixtureRequest) -> str:
    worker_input = getattr(request.config, "workerinput", None)
    if worker_input is None:
        return os.getenv(
            CONNECTION_URL_ENV,
            DEFAULT_CONNECTION_URL,
        )
    worker_id = str(worker_input["workerid"])
    worker_index = int(worker_id.removeprefix("gw"))
    return f"udpin://0.0.0.0:{14540 + worker_index}"


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[Any]) -> Any:
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture
def vehicle(request: pytest.FixtureRequest) -> Iterator[Vehicle]:
    client = VehicleClient(connection_url=get_connection_url(request))
    client.connect()
    drone = client.get_drone()

    telemetry = TelemetryMonitor(drone)
    actions = VehicleActions(drone)
    parameters = VehicleParameters(drone)
    mission = VehicleMission(drone)
    failures = VehicleFailures(drone)
    info = VehicleInfo(drone)
    connected_vehicle = Vehicle(
        actions,
        telemetry,
        parameters,
        mission,
        failures,
        info,
    )

    telemetry.start()
    cleanup_errors: list[Exception] = []
    try:
        yield connected_vehicle
    finally:
        try:
            connected_vehicle.reset_test_state()
        except Exception as error:
            cleanup_errors.append(error)
            logger.warning(
                "Failed to reset vehicle test state: %s",
                error,
            )

        try:
            telemetry.stop()
        except Exception as error:
            cleanup_errors.append(error)
            logger.warning(
                "Failed to stop telemetry: %s",
                error,
            )

        call_report = getattr(request.node, "rep_call", None)
        test_failed = call_report is not None and call_report.failed
        if cleanup_errors and not test_failed:
            if len(cleanup_errors) == 1:
                raise cleanup_errors[0]
            raise ExceptionGroup(
                "Failed to clean up vehicle fixture",
                cleanup_errors,
            )
