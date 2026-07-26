#!/usr/bin/env python3
"""One-click ARES Phase-0 demo: VcXsrv + Gazebo GUI + PX4 SITL + MAVSDK takeoff/land."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
VCXSRV = Path(r"C:\Program Files\VcXsrv\vcxsrv.exe")
WSL_DISTRO = "Ubuntu"
WSL_USER = "sunny"
READY_MARKERS = (
    "Ready for takeoff",
    "Startup script returned successfully",
)
FAIL_MARKERS = (
    "Gazebo GUI failed",
    "Gazebo failed",
    "gz_bridge failed to start",
)


def win_to_wsl(path: Path) -> str:
    """Convert C:\\Users\\... to /mnt/c/Users/..."""
    resolved = path.resolve()
    s = str(resolved).replace("\\", "/")
    if len(s) >= 2 and s[1] == ":":
        return f"/mnt/{s[0].lower()}{s[2:]}"
    return s


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, **kwargs)


def ensure_vcxsrv() -> None:
    if not VCXSRV.exists():
        print(f"[!] VcXsrv not found at: {VCXSRV}")
        print("    Install VcXsrv first, then re-run.")
        sys.exit(1)

    check = run(
        ["tasklist", "/FI", "IMAGENAME eq vcxsrv.exe"],
        capture_output=True,
        text=True,
    )
    if "vcxsrv.exe" in (check.stdout or "").lower():
        print("[*] VcXsrv already running")
        return

    print("[*] Starting VcXsrv...")
    subprocess.Popen(
        [str(VCXSRV), ":0", "-multiwindow", "-clipboard", "-wgl", "-ac"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2)


def wsl(cmd: str) -> subprocess.CompletedProcess:
    return run(
        ["wsl", "-d", WSL_DISTRO, "-u", WSL_USER, "--", "bash", "-lc", cmd],
        text=True,
        capture_output=True,
    )


def stop_sim() -> None:
    print("[*] Stopping previous sim processes (if any)...")
    wsl("killall -q px4 gz gz-sim gz-sim-server ruby 2>/dev/null || true")
    time.sleep(1)


def start_sitl() -> subprocess.Popen:
    log_win = ROOT / "_ares_demo_sitl.log"
    if log_win.exists():
        log_win.unlink()

    sitl_sh = win_to_wsl(SCRIPTS / "start_sitl_gui.sh")
    demo_py = win_to_wsl(SCRIPTS / "mavsdk_takeoff_land.py")
    log_wsl = win_to_wsl(log_win)

    prep = wsl(
        f"cp '{sitl_sh}' ~/ares_start_sitl_gui.sh && "
        f"cp '{demo_py}' ~/ares_mavsdk_takeoff_land.py && "
        "chmod +x ~/ares_start_sitl_gui.sh ~/ares_mavsdk_takeoff_land.py"
    )
    if prep.returncode != 0:
        print(prep.stderr or prep.stdout)
        sys.exit(1)

    print("[*] Starting Gazebo GUI + PX4 (look for Gazebo window)...")
    cmd = f"bash ~/ares_start_sitl_gui.sh 2>&1 | tee '{log_wsl}'"
    return subprocess.Popen(
        ["wsl", "-d", WSL_DISTRO, "-u", WSL_USER, "--", "bash", "-lc", cmd],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )


def wait_ready(timeout_s: int = 180) -> None:
    log_path = ROOT / "_ares_demo_sitl.log"
    print(f"[*] Waiting up to {timeout_s}s for PX4 ready...")
    start = time.time()
    last_size = 0
    while time.time() - start < timeout_s:
        if log_path.exists():
            text = log_path.read_text(encoding="utf-8", errors="ignore")
            if len(text) != last_size:
                last_size = len(text)
                lines = [ln for ln in text.splitlines() if ln.strip()]
                if lines:
                    print(f"    ... {lines[-1][:120]}")
            for bad in FAIL_MARKERS:
                if bad in text:
                    print(f"[!] SITL failed: {bad}")
                    sys.exit(1)
            for ok in READY_MARKERS:
                if ok in text:
                    print(f"[*] Ready marker seen: {ok}")
                    time.sleep(3)
                    return
        time.sleep(2)
    print("[!] Timed out waiting for SITL ready. Check _ares_demo_sitl.log")
    sys.exit(1)


def run_mavsdk() -> None:
    print("[*] Running MAVSDK takeoff/land demo...")
    result = run(
        [
            "wsl",
            "-d",
            WSL_DISTRO,
            "-u",
            WSL_USER,
            "--",
            "bash",
            "-lc",
            "source ~/ares-venv/bin/activate && python3 ~/ares_mavsdk_takeoff_land.py",
        ],
        text=True,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0 or "STEP9_OK" not in (result.stdout or ""):
        print("[!] MAVSDK demo did not complete successfully")
        sys.exit(result.returncode or 1)
    print("[*] MAVSDK demo OK")


def main() -> int:
    print("=== ARES-UAV one-command demo ===")
    if not (SCRIPTS / "start_sitl_gui.sh").exists():
        print(f"[!] Missing {SCRIPTS / 'start_sitl_gui.sh'}")
        sys.exit(1)

    ensure_vcxsrv()
    stop_sim()
    sitl = start_sitl()
    try:
        wait_ready()
        run_mavsdk()
        print()
        print("SUCCESS: takeoff/land completed.")
        print("Close this window when finished watching Gazebo.")
        return 0
    finally:
        print("[*] Stopping sim...")
        stop_sim()
        if sitl.poll() is None:
            try:
                sitl.send_signal(signal.CTRL_BREAK_EVENT)  # type: ignore[attr-defined]
            except Exception:
                sitl.terminate()
            try:
                sitl.wait(timeout=5)
            except Exception:
                sitl.kill()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nInterrupted.")
        stop_sim()
        raise SystemExit(130)
