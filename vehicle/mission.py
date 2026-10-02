from __future__ import annotations

from mavsdk import System
from mavsdk.plugins.mission import Mission, MissionPlan, MissionProgress


class VehicleMission:
    def __init__(self, drone: System) -> None:
        self._mission = Mission(drone)

    def upload(self, mission_plan: MissionPlan) -> None:
        self._mission.upload_mission(mission_plan)

    def download(self) -> MissionPlan:
        return self._mission.download_mission()

    def start(self) -> None:
        self._mission.start_mission()

    def pause(self) -> None:
        self._mission.pause_mission()

    def clear(self) -> None:
        self._mission.clear_mission()

    def set_current_item(self, index: int) -> None:
        self._mission.set_current_mission_item(index)

    def set_return_to_launch_after_mission(self, enabled: bool) -> None:
        self._mission.set_return_to_launch_after_mission(enabled)

    def get_return_to_launch_after_mission(self) -> bool:
        return bool(self._mission.get_return_to_launch_after_mission())

    def is_finished(self) -> bool:
        return bool(self._mission.is_mission_finished())

    def get_progress(self) -> MissionProgress:
        return self._mission.mission_progress()

    def get_current_item_index(self) -> int:
        return int(self.get_progress().current)

    def get_total_items_count(self) -> int:
        return int(self.get_progress().total)

    def get_progress_fraction(self) -> float:
        progress = self.get_progress()
        if progress.total == 0:
            return 0.0
        return float(progress.current / progress.total)

    def get_progress_percent(self) -> float:
        return self.get_progress_fraction() * 100.0
