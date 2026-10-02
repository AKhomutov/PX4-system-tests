from __future__ import annotations

import time
from collections.abc import Callable


def wait_until(
    condition: Callable[[], bool],
    timeout_s: float,
    description: str,
) -> None:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if condition():
            return
        time.sleep(0.1)

    raise TimeoutError(f"Timed out after {timeout_s}s waiting for {description}")
