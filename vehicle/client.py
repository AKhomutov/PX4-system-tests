from __future__ import annotations

from mavsdk import ComponentType, Configuration, Mavsdk, System

DEFAULT_CONNECTION_URL = "udpin://0.0.0.0:14540"
CONNECTION_URL_ENV = "PX4_CONNECTION_URL"


class VehicleClient:
    def __init__(self, connection_url: str = DEFAULT_CONNECTION_URL) -> None:
        self.connection_url = connection_url
        self.sdk: Mavsdk | None = None
        self.drone: System | None = None

    def _create_sdk(self) -> None:
        config = Configuration.create_with_component_type(
            ComponentType.GROUND_STATION
        )

        self.sdk = Mavsdk(config)

        self.sdk.add_any_connection(self.connection_url)

    def _discover_drone(self) -> None:
        if self.sdk is None:
            raise RuntimeError("SDK is not created")

        self.drone = self.sdk.first_autopilot(10.0)

        if self.drone is None:
            raise RuntimeError("No autopilot found")

        print("PX4 autopilot discovered")

    def get_drone(self) -> System:
        if self.drone is None:
            raise RuntimeError("Vehicle is not connected")
        return self.drone

    def connect(self) -> None:
        self._create_sdk()
        self._discover_drone()
