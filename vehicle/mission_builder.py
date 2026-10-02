from __future__ import annotations

import math
from dataclasses import dataclass

from mavsdk.plugins.mission import MissionItem, MissionPlan


@dataclass(frozen=True)
class Waypoint:
    latitude_deg: float
    longitude_deg: float
    relative_altitude_m: float
    speed_m_s: float = math.nan
    is_fly_through: bool = True
    yaw_deg: float = math.nan
    acceptance_radius_m: float = math.nan


class MissionBuilder:
    def __init__(self) -> None:
        self._items: list[MissionItem] = []

    def add_waypoint(
        self,
        latitude_deg: float,
        longitude_deg: float,
        relative_altitude_m: float,
        *,
        speed_m_s: float = math.nan,
        is_fly_through: bool = True,
        yaw_deg: float = math.nan,
        acceptance_radius_m: float = math.nan,
    ) -> MissionBuilder:
        self._items.append(
            MissionItem(
                latitude_deg=latitude_deg,
                longitude_deg=longitude_deg,
                relative_altitude_m=relative_altitude_m,
                speed_m_s=speed_m_s,
                is_fly_through=is_fly_through,
                gimbal_pitch_deg=math.nan,
                gimbal_yaw_deg=math.nan,
                camera_action=MissionItem.CameraAction.NONE,
                loiter_time_s=math.nan,
                camera_photo_interval_s=math.nan,
                acceptance_radius_m=acceptance_radius_m,
                yaw_deg=yaw_deg,
                camera_photo_distance_m=math.nan,
                vehicle_action=MissionItem.VehicleAction.NONE,
            )
        )
        return self

    def add_waypoints(self, waypoints: list[Waypoint]) -> MissionBuilder:
        for waypoint in waypoints:
            self.add_waypoint(
                waypoint.latitude_deg,
                waypoint.longitude_deg,
                waypoint.relative_altitude_m,
                speed_m_s=waypoint.speed_m_s,
                is_fly_through=waypoint.is_fly_through,
                yaw_deg=waypoint.yaw_deg,
                acceptance_radius_m=waypoint.acceptance_radius_m,
            )
        return self

    def build(self) -> MissionPlan:
        if not self._items:
            raise ValueError("Mission plan must contain at least one waypoint")
        return MissionPlan(self._items)
