# PX4 System Tests

Small system/integration test project for PX4 using Python, MAVSDK, pytest, PX4 SITL and Gazebo.

The main idea is to test PX4 through external interfaces rather than internal implementation details: actions, telemetry, parameters, missions and failure injection.

## Covered scenarios

Current tests cover:

- vehicle readiness checks;
- takeoff and landing;
- Return-to-Launch;
- configurable takeoff altitude;
- mission execution and pause;
- GPS failure injection;
- vehicle/firmware information.

Tests run against PX4 SITL with Gazebo.

## Structure

```text
tests/
vehicle/
utils/
```

`vehicle/` contains small wrappers around MAVSDK functionality:

- actions
- telemetry
- parameters
- missions
- failure injection
- vehicle info

`Vehicle` acts as the main facade used by tests.

Example:

```python
vehicle.wait_for_position()

vehicle.arm()
vehicle.take_off()
vehicle.verify_altitude_is_above(2.0)

vehicle.actions.return_to_launch()

vehicle.verify_is_on_ground()
vehicle.verify_is_disarmed()
```

## Missions

Mission plans can be built with `MissionBuilder`:

```python
mission_plan = (
    MissionBuilder()
    .add_waypoint(latitude + 0.00005, longitude, 5.0)
    .add_waypoint(latitude + 0.00005, longitude + 0.00005, 5.0)
    .build()
)

vehicle.mission.upload(mission_plan)
vehicle.arm()
vehicle.mission.start()

vehicle.verify_mission_finished()
```

## Failure injection

MAVSDK failure injection is wrapped in `VehicleFailures`.

Example:

```python
vehicle.failures.fail_gps(FailureType.OFF)

wait_until(
    lambda: not vehicle.telemetry.is_global_position_ok(),
    timeout_s=10.0,
    description="global position to become unhealthy after GPS failure",
)
```

Injected failures are restored automatically during test cleanup.

## Test cleanup

The pytest fixture tries to leave PX4 in a clean state after every test:

- restore injected failures;
- land/disarm the vehicle;
- clear missions;
- stop telemetry subscriptions.

This also runs when a test fails.

## Local setup

### PX4 SITL + Gazebo

Launcher scripts are available in `scripts/`:

```bash
./scripts/run_px4_sitl_nvidia.sh
./scripts/run_px4_sitl_amd.sh
./scripts/run_px4_sitl_cpu.sh
```

The NVIDIA version requires Docker with NVIDIA Container Toolkit configured.

The scripts start PX4 SITL with the Gazebo `gz_x500` model and use host networking so MAVSDK can connect over UDP.

### QGroundControl

Download the Linux AppImage from the official QGroundControl release page.

Make it executable and run it:

```bash
chmod +x QGroundControl.AppImage
./QGroundControl.AppImage
```

QGroundControl is optional for automated tests, but useful for monitoring the simulated vehicle and manual inspection.

### Python environment

```bash
python -m venv .venv
source .venv/bin/activate
```

Then install the project dependencies and run:

```bash
pip install -e ".[dev]"
pytest -v
```

Static checks:

```bash
ruff check .
mypy .
```

## Tech stack

Python 3.14, pytest, MAVSDK, PX4 SITL, Gazebo, Ruff and mypy.
