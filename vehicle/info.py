from __future__ import annotations

from mavsdk import System
from mavsdk.plugins.info import Identification, Info, Product, Version


class VehicleInfo:
    def __init__(self, drone: System) -> None:
        self._info = Info(drone)

    def get_identification(self) -> Identification:
        return self._info.get_identification()

    def get_product(self) -> Product:
        return self._info.get_product()

    def get_version(self) -> Version:
        return self._info.get_version()

    def get_speed_factor(self) -> float:
        return float(self._info.get_speed_factor())

    def get_hardware_uid(self) -> str:
        return str(self.get_identification().hardware_uid)

    def get_legacy_uid(self) -> int:
        return int(self.get_identification().legacy_uid)

    def get_vendor_id(self) -> int:
        return int(self.get_product().vendor_id)

    def get_vendor_name(self) -> str:
        return str(self.get_product().vendor_name)

    def get_product_id(self) -> int:
        return int(self.get_product().product_id)

    def get_product_name(self) -> str:
        return str(self.get_product().product_name)

    def get_flight_software_version(self) -> str:
        version = self.get_version()
        return (
            f"{int(version.flight_sw_major)}."
            f"{int(version.flight_sw_minor)}."
            f"{int(version.flight_sw_patch)}"
        )

    def get_flight_software_git_hash(self) -> str:
        return str(self.get_version().flight_sw_git_hash)
