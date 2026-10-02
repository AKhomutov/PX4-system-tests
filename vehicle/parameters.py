from __future__ import annotations

from mavsdk import System
from mavsdk.plugins.param import Param, ParamError, ParamResult

_WRONG_TYPE_RESULTS = frozenset(
    {
        ParamResult.WRONG_TYPE,
        ParamResult.TYPE_MISMATCH,
        ParamResult.TYPE_UNSUPPORTED,
    }
)


class VehicleParameters:
    def __init__(self, drone: System) -> None:
        self._param = Param(drone)

    def get_int(self, name: str) -> int:
        return int(self._param.get_param_int(name))

    def get_float(self, name: str) -> float:
        return float(self._param.get_param_float(name))

    def set_int(self, name: str, value: int) -> None:
        self._param.set_param_int(name, value)

    def set_float(self, name: str, value: float) -> None:
        self._param.set_param_float(name, value)

    def get_value(self, name: str) -> int | float:
        try:
            return self.get_int(name)
        except ParamError as error:
            if error.result not in _WRONG_TYPE_RESULTS:
                raise
            return self.get_float(name)

    def restore(self, name: str, value: int | float) -> None:
        if isinstance(value, bool):
            raise TypeError(f"Unsupported param value type for {name!r}: bool")
        if isinstance(value, int):
            self.set_int(name, value)
        else:
            self.set_float(name, value)
