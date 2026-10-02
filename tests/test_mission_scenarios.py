from __future__ import annotations

import time

from vehicle.mission_builder import MissionBuilder
from vehicle.vehicle import Vehicle


def test_simple_mission_completes(vehicle: Vehicle) -> None:
    vehicle.wait_for_position()

    latitude = vehicle.telemetry.get_latitude_deg()
    longitude = vehicle.telemetry.get_longitude_deg()

    mission_plan = (
        MissionBuilder()
        .add_waypoint(latitude + 0.00005, longitude, 5.0)
        .add_waypoint(latitude + 0.00005, longitude + 0.00005, 5.0)
        .build()
    )

    vehicle.mission.upload(mission_plan)

    vehicle.arm()
    vehicle.mission.start()

    vehicle.verify_mission_progress_at_least(0.5)
    vehicle.verify_mission_finished()


def test_mission_can_be_paused(vehicle: Vehicle) -> None:
    vehicle.wait_for_position()

    latitude = vehicle.telemetry.get_latitude_deg()
    longitude = vehicle.telemetry.get_longitude_deg()

    mission_plan = (
        MissionBuilder()
        .add_waypoint(latitude + 0.00010, longitude, 5.0)
        .add_waypoint(latitude + 0.00010, longitude + 0.00010, 5.0)
        .add_waypoint(latitude, longitude + 0.00010, 5.0)
        .build()
    )

    vehicle.mission.upload(mission_plan)
    vehicle.arm()
    vehicle.mission.start()

    vehicle.verify_mission_progress_at_least(1 / 3)

    vehicle.mission.pause()

    progress_after_pause = vehicle.mission.get_progress_fraction()
    time.sleep(2.0)

    assert vehicle.mission.get_progress_fraction() == progress_after_pause
