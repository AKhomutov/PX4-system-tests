from __future__ import annotations

from mavsdk import System
from mavsdk.plugins.failure import Failure, FailureType, FailureUnit


class VehicleFailures:
    def __init__(self, drone: System) -> None:
        self._failure = Failure(drone)
        self._injected: set[tuple[FailureUnit, int]] = set()

    def inject(
        self,
        unit: FailureUnit,
        failure_type: FailureType,
        instance: int = 0,
    ) -> None:
        self._failure.inject(unit, failure_type, instance)

        if failure_type == FailureType.OK:
            self._injected.discard((unit, instance))
        else:
            self._injected.add((unit, instance))

    def fail_gps(
        self,
        failure_type: FailureType,
        instance: int = 0,
    ) -> None:
        self.inject(FailureUnit.SENSOR_GPS, failure_type, instance)

    def fail_gyro(
        self,
        failure_type: FailureType,
        instance: int = 0,
    ) -> None:
        self.inject(FailureUnit.SENSOR_GYRO, failure_type, instance)

    def fail_accelerometer(
        self,
        failure_type: FailureType,
        instance: int = 0,
    ) -> None:
        self.inject(FailureUnit.SENSOR_ACCEL, failure_type, instance)

    def fail_motor(
        self,
        failure_type: FailureType,
        instance: int = 0,
    ) -> None:
        self.inject(FailureUnit.SYSTEM_MOTOR, failure_type, instance)

    def fail_barometer(
        self,
        failure_type: FailureType,
        instance: int = 0,
    ) -> None:
        self.inject(FailureUnit.SENSOR_BARO, failure_type, instance)

    def restore_gps(self, instance: int = 0) -> None:
        self.inject(FailureUnit.SENSOR_GPS, FailureType.OK, instance)

    def restore_gyro(self, instance: int = 0) -> None:
        self.inject(FailureUnit.SENSOR_GYRO, FailureType.OK, instance)

    def restore_accelerometer(self, instance: int = 0) -> None:
        self.inject(FailureUnit.SENSOR_ACCEL, FailureType.OK, instance)

    def restore_motor(self, instance: int = 0) -> None:
        self.inject(FailureUnit.SYSTEM_MOTOR, FailureType.OK, instance)

    def restore_barometer(self, instance: int = 0) -> None:
        self.inject(FailureUnit.SENSOR_BARO, FailureType.OK, instance)

    def restore_all(self) -> None:
        errors: list[Exception] = []

        for unit, instance in list(self._injected):
            try:
                self.inject(unit, FailureType.OK, instance)
            except Exception as error:
                errors.append(error)

        if len(errors) == 1:
            raise errors[0]
        if errors:
            raise ExceptionGroup("Failed to restore injected failures", errors)
