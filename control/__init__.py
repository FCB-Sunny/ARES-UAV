"""L2 flight-control interface (MAVSDK wrappers).

Import submodules directly (e.g. control.vehicle) when possible.
Package __init__ stays light so non-flight tools need not load MAVSDK.
"""

__all__ = ["Vehicle", "run_mission"]


def __getattr__(name: str):
    if name == "Vehicle":
        from control.vehicle import Vehicle

        return Vehicle
    if name == "run_mission":
        from control.mission_runner import run_mission

        return run_mission
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
