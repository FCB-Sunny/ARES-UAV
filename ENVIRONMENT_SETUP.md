# ARES-UAV — Environment Setup Plan (Phase 0)

**Status:** PLAN ONLY — do not install until human confirmation  
**Created:** 2026-07-25  
**Host analysis date:** 2026-07-25  

This document defines the complete development environment for ARES-UAV.  
It is the engineering foundation before autonomy, swarm, or AI code.

---

## 1. Host Environment Analysis (Current Machine)

| Item | Detected value | Assessment |
|------|----------------|------------|
| OS | Windows 10 Pro, Build **19045** (x64) | Supported for WSL2 |
| CPU | Intel Core **i5-7500** @ 3.40 GHz (4C/4T) | Adequate for **1 drone** SITL; tight for multi-drone |
| RAM | **16 GB** total (~3.4 GB free at scan time) | Minimum viable; close heavy apps before simulation |
| GPU | Intel HD Graphics 630 + **Radeon RX 550** | Weak for ML training; usable for Gazebo GUI via WSLg if configured. Treat deep learning as **CPU / cloud later** |
| Storage C: | ~**123 GB** free / ~300 GB | Enough for WSL + stack if kept clean |
| Storage D: | ~**291 GB** free | Preferred location for large WSL/PX4 data if C: gets tight |
| Storage E: | ~**194 GB** free | Project workspace drive (current mission folder) |
| Virtualization | Hypervisor detected | Ready for WSL2 |
| WSL | Default version **2**; **kernel file missing**; **no distros installed** | Must install/update WSL2 kernel + Ubuntu 22.04 first |

### Compatibility verdict

| Goal | Verdict |
|------|---------|
| WSL2 + Ubuntu 22.04 | Compatible after kernel install |
| ROS 2 Humble | Compatible (official platform = Ubuntu 22.04) |
| PX4 SITL + Gazebo | Compatible for single-vehicle first |
| MAVSDK Python control | Compatible |
| Local YOLO training / Isaac Sim | **Not** recommended on this host |
| Swarm (3–5 drones) later | Possible with reduced Gazebo fidelity / headless; may need more RAM |

### Design constraints derived from hardware

1. Prefer **headless** Gazebo for long runs; use GUI only for demos.  
2. Cap first milestone at **1 PX4 instance**.  
3. Do **not** install CUDA, Isaac Sim, or local LLM runtimes in Phase 0.  
4. Allocate WSL memory explicitly (see §8) so Windows does not starve.

---

## 2. Recommended Software Architecture

```
Windows 10 Pro (Build 19045)
    |
    |  WSLg (GUI apps) + WSL2 kernel
    v
WSL2
    |
    v
Ubuntu 22.04 LTS
    |
    +-- ROS 2 Humble Hawksbill          # middleware, packages, tooling
    |
    +-- Gazebo Harmonic (gz-sim)        # physics + sensors
    |       |
    |       +-- ros_gz bridge           # ROS 2 <-> Gazebo
    |
    +-- PX4 Autopilot (SITL)            # flight stack / firmware sim
    |
    +-- MAVLink tools (pymavlink)       # protocol utilities / debugging
    |
    +-- MAVSDK (Python)                 # high-level drone API for ARES
    |
    v
ARES-UAV application layers (later phases)
    autonomy / swarm / perception / ai_agent / control
```

### Why this stack (and not alternatives)

| Choice | Why |
|--------|-----|
| **WSL2 + Ubuntu 22.04** | Native ROS 2 / PX4 docs target Linux. Avoids fragile native Windows robotics installs. |
| **ROS 2 Humble** | LTS; best documented with Ubuntu 22.04; long support window for ARES development. |
| **Gazebo Harmonic** | Current PX4-recommended Gazebo family on Ubuntu 22.04; aligns with project vision. |
| **PX4 SITL** | Industry-standard autopilot sim; offboard + MAVLink ready for autonomy. |
| **MAVSDK Python** | Cleaner API than raw MAVLink for mission scripts; official PX4 companion. |
| **pymavlink** | Low-level debugging / custom MAVLink when MAVSDK is insufficient. |

| Rejected (Phase 0) | Why not |
|--------------------|---------|
| Isaac Sim | Heavy GPU/CPU; overkill; conflicts with “no training GPU” constraint |
| ROS 1 / Melodic | End of life; not future-compatible |
| Gazebo Classic only | Still usable fallback, but Harmonic is the forward path for PX4 |
| Docker-first everything | Adds complexity before first flight; optional later for CI |
| Native Windows ROS | Poor PX4/Gazebo support compared to Ubuntu |

### Optional fallback (document only)

If Harmonic + WSLg is too slow on this CPU: use **Gazebo Classic (gz11)** with PX4’s classic targets. Prefer Harmonic first; switch only if performance blocks Phase 1.

---

## 3. Required Software List

### 3.1 Windows host

| Software | Recommended version | Purpose |
|----------|---------------------|---------|
| WSL2 | Latest via `wsl --update` | Linux VM |
| Ubuntu | **22.04 LTS** | ROS 2 Humble platform |
| Windows Terminal (optional) | Latest Store | Better multi-pane UX |
| Git for Windows (optional) | Latest | Host-side git; also install git inside WSL |
| VS Code / Cursor | Current | Edit repo; Remote-WSL optional |

### 3.2 Inside Ubuntu 22.04 (WSL2)

| Component | Recommended version | Purpose |
|-----------|---------------------|---------|
| Build tools | `build-essential`, `cmake`, `git` | Compile PX4 & packages |
| Python | **3.10** (Ubuntu 22.04 default) | MAVSDK, ARES scripts |
| ROS 2 | **Humble Hawksbill** (desktop or desktop-full) | Robotics middleware |
| Gazebo | **Harmonic** (`gz-harmonic`) | Simulation |
| ros_gz | Matching Humble packages | Bridge ROS 2 ↔ Gazebo |
| PX4 Autopilot | Stable release branch (e.g. **v1.15.x** or latest stable tag at install time) | SITL firmware |
| MAVSDK Python | Latest `mavsdk` on PyPI compatible with PX4 | Offboard / missions |
| pymavlink | Latest stable | MAVLink debug |
| colcon / vcstool | ROS 2 defaults | Workspace builds |

### 3.3 Explicitly NOT installing in Phase 0

- NVIDIA CUDA / TensorRT  
- Isaac Sim  
- Local Llama / large LLM runtimes  
- Deep learning training stacks (PyTorch CUDA)  
- Kubernetes / heavy orchestration  

---

## 4. Installation Order (Strict)

Install in this order. Each step depends on the previous.

| Step | Component | Depends on |
|------|-----------|------------|
| 0 | Snapshot / rollback prep | — |
| 1 | WSL2 kernel update + enable features | Windows admin |
| 2 | Ubuntu 22.04 distro | WSL2 kernel |
| 3 | WSL resource config (`.wslconfig`) | Ubuntu installed |
| 4 | Ubuntu base packages + Python venv tooling | Ubuntu |
| 5 | ROS 2 Humble | Ubuntu base |
| 6 | Gazebo Harmonic + ros_gz | ROS 2 |
| 7 | PX4 Autopilot + dependencies | Ubuntu + build tools |
| 8 | MAVSDK Python + pymavlink | Python 3.10 |
| 9 | End-to-end verification (PX4 SITL ↔ MAVSDK) | Steps 5–8 |
| 10 | Document versions / freeze notes | Success of step 9 |

**Do not** install PX4 before ROS/Gazebo unless diagnosing networking only — full ARES path needs the whole stack.

---

## 5. Dependency Explanation

```
WSL2 kernel
  → Ubuntu 22.04 userland
    → apt packages (compilers, python3-pip, etc.)
      → ROS 2 Humble (middleware + rclpy)
        → Gazebo Harmonic (simulator process)
          → ros_gz (topic/service bridge)
            → PX4 SITL (talks MAVLink UDP; may use Gazebo plugins)
              → MAVSDK (connects to PX4 MAVLink endpoint)
                → ARES Python nodes (future)
```

**Networking note (critical on WSL2):**  
PX4 SITL typically listens on `UDP 14540` (companion) / `14550` (GCS).  
MAVSDK in the **same** WSL instance should use `udp://:14540` (or PX4-documented endpoint).  
Avoid mixing Windows-host MAVSDK with WSL PX4 until port forwarding is deliberately configured.

---

## 6. Commands to Install Each Component

> **Policy:** Commands below are the approved plan. Execute only after human confirmation.  
> Run robotics installs **inside Ubuntu 22.04 (WSL)**, except Step 1 (Windows PowerShell **Admin**).

### Step 0 — Backup / rollback prep (Windows)

```powershell
# From elevated PowerShell (optional but recommended)
Checkpoint-Computer -Description "Before-ARES-UAV-WSL" -RestorePointType "MODIFY_SETTINGS"
```

If System Restore is disabled, at minimum note:

- Free disk space on C:/D:  
- That no Ubuntu distro exists yet (clean install)  
- Plan to remove distro with `wsl --unregister Ubuntu-22.04` if setup fails (see §9)

### Step 1 — WSL2 kernel + platform (Windows Admin PowerShell)

```powershell
wsl --install --no-distribution
wsl --update
wsl --set-default-version 2
wsl --status
```

**Why:** Host scan shows WSL default v2 but **kernel file missing** and **no distros**. This step restores the kernel.

### Step 2 — Ubuntu 22.04

```powershell
wsl --install -d Ubuntu-22.04
```

Complete first-boot username/password in the Ubuntu window, then:

```powershell
wsl -l -v
```

Expect `Ubuntu-22.04` with `VERSION = 2`.

### Step 3 — WSL resource limits (Windows)

Create/edit `%UserProfile%\.wslconfig`:

```ini
[wsl2]
memory=10GB
processors=4
swap=8GB
localhostForwarding=true

[experimental]
guiApplications=true
```

Then:

```powershell
wsl --shutdown
```

**Why:** 16 GB host RAM — give WSL ~10 GB so Gazebo + PX4 can run without freezing Windows. Adjust to `8GB` if the host feels unstable.

### Step 4 — Ubuntu base packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
  build-essential cmake git wget curl \
  python3-pip python3-venv python3-dev \
  python3-argcomplete \
  ca-certificates gnupg lsb-release \
  mesa-utils
```

**Verify:**

```bash
uname -a
lsb_release -a
python3 --version   # expect 3.10.x
gcc --version
```

### Step 5 — ROS 2 Humble

Follow official ROS 2 Humble apt install (locale + sources + packages):

```bash
sudo apt install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

sudo apt install -y software-properties-common
sudo add-apt-repository universe -y

sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | \
  sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

sudo apt update
sudo apt install -y ros-humble-desktop
sudo apt install -y ros-dev-tools python3-colcon-common-extensions
```

Add to `~/.bashrc`:

```bash
source /opt/ros/humble/setup.bash
```

**Verify:**

```bash
source /opt/ros/humble/setup.bash
ros2 --help
# In two terminals:
# ros2 run demo_nodes_cpp talker
# ros2 run demo_nodes_py listener
```

**Why `ros-humble-desktop`:** Includes RViz and common tools needed later for autonomy visualization, without jumping to full simulation meta-packages prematurely.

### Step 6 — Gazebo Harmonic + ROS-Gazebo bridge

```bash
sudo apt install -y gz-harmonic
sudo apt install -y ros-humble-ros-gz
```

**Verify:**

```bash
gz sim --versions
# GUI test (WSLg):
gz sim -r shapes.sdf
# Or headless smoke test:
gz sim -s -r shapes.sdf
```

**Why Harmonic:** Matches PX4’s current Gazebo path and ARES architecture docs.  
**Why ros-humble-ros-gz:** Required later for camera/lidar topics into ROS 2 perception nodes.

### Step 7 — PX4 Autopilot (SITL)

```bash
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
cd PX4-Autopilot
git checkout v1.15.4   # pin a known stable tag at install time; replace if newer patch exists
git submodule update --init --recursive

bash ./Tools/setup/ubuntu.sh
```

Build SITL (Gazebo Harmonic target — confirm exact make target from PX4 docs for the checked-out tag):

```bash
cd ~/PX4-Autopilot
make px4_sitl gz_x500
```

**Verify:**

```bash
# PX4 console should start; wait until "Ready to fly" / navigator ready messages
# Default companion MAVLink often on UDP 14540
```

Leave this running for MAVSDK tests, or run headless if GUI is slow.

**Why pin a release tag:** Reproducibility for ARES; avoid silent `main` breakage.

### Step 8 — MAVSDK Python + MAVLink tools

```bash
python3 -m venv ~/ares-venv
source ~/ares-venv/bin/activate
pip install --upgrade pip
pip install mavsdk pymavlink
```

**Verify:**

```bash
python -c "import mavsdk; print('mavsdk OK')"
python -c "import pymavlink; print('pymavlink OK')"
```

**Why venv:** Isolates ARES Python deps from apt/ROS Python packages.

### Step 9 — Minimal MAVSDK takeoff check (acceptance)

With PX4 SITL running (`make px4_sitl gz_x500`):

```bash
source ~/ares-venv/bin/activate
python3 << 'EOF'
import asyncio
from mavsdk import System

async def main():
    drone = System()
    await drone.connect(system_address="udp://:14540")
    print("Waiting for drone...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Connected")
            break
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("Health OK")
            break
    print("Arming...")
    await drone.action.arm()
    print("Taking off...")
    await drone.action.takeoff()
    await asyncio.sleep(8)
    print("Landing...")
    await drone.action.land()
    await asyncio.sleep(8)
    print("MAVSDK control OK")

asyncio.run(main())
EOF
```

**Success criteria for Phase 0:**

1. `ros2` commands work  
2. `gz sim` launches (GUI or headless)  
3. PX4 SITL starts  
4. MAVSDK script arms, takes off, lands  
5. No autonomy/swarm code required yet  

---

## 7. Verification Checklist (After Each Step)

| Step | Verification command / action | Pass criteria |
|------|-------------------------------|---------------|
| 1 WSL kernel | `wsl --status` | No “kernel file is not found” |
| 2 Ubuntu | `wsl -l -v` | Ubuntu-22.04, VERSION 2 |
| 3 `.wslconfig` | `wsl --shutdown` then reopen; `free -h` in Ubuntu | Memory ≈ configured limit |
| 4 Base pkgs | `python3 --version`, `gcc --version` | 3.10.x, gcc present |
| 5 ROS 2 | talker/listener demo | Messages received |
| 6 Gazebo | `gz sim -s -r shapes.sdf` | Process starts without crash |
| 7 PX4 | `make px4_sitl gz_x500` | SITL reaches ready state |
| 8 MAVSDK | `import mavsdk` | No import error |
| 9 E2E | takeoff script | Arm → takeoff → land |

Record installed versions in `docs/ENV_VERSIONS.md` after success (future small doc; not required before install confirmation).

---

## 8. Performance Guidance for This Host

| Setting | Recommendation |
|---------|----------------|
| Simultaneous drones (Phase 0–1) | **1 only** |
| Gazebo GUI | Use for demos; prefer `-s` headless while developing |
| Browser / Chrome tabs | Close before SITL |
| WSL memory | 8–10 GB |
| Swap | 8 GB |
| Antivirus realtime scan | Exclude WSL VHDX / `PX4-Autopilot` build dir if builds are very slow |

---

## 9. Common Problems and Solutions

| Problem | Likely cause | Solution |
|---------|--------------|----------|
| `The WSL 2 kernel file is not found` | Missing/outdated WSL kernel | `wsl --update` as Admin; reboot |
| `wsl --install` fails | Virtual Machine Platform disabled | Enable “Virtual Machine Platform” + “Windows Subsystem for Linux” in Windows Features; reboot |
| Ubuntu installs as WSL1 | Default version not set | `wsl --set-default-version 2` then `wsl --set-version Ubuntu-22.04 2` |
| `gz sim` / GUI blank | WSLg not active | Update WSL; set `guiApplications=true`; `wsl --shutdown` |
| Gazebo very slow | CPU-bound + GUI | Run headless; lower update rate; single vehicle |
| ROS 2 domain interference | Multiple ROS sessions | Set `ROS_DOMAIN_ID=42` in `~/.bashrc` for ARES |
| MAVSDK never connects | Wrong UDP port / PX4 not ready | Confirm PX4 ready; use `udp://:14540`; same WSL instance |
| `make px4_sitl` build errors | Incomplete submodules / missing deps | Re-run `ubuntu.sh`; `git submodule update --init --recursive` |
| Host freezes during sim | RAM exhaustion | Lower `.wslconfig` memory? Actually **reduce** Gazebo load; close apps; ensure swap exists |
| Disk full on C: | WSL VHDX growth | Move distro to D: (`wsl --export` / `--import`) |
| apt ROS key/hash errors | Clock skew / mirror | `sudo timedatectl` / retry `apt update` |

---

## 10. Backup / Rollback Approach

### Soft rollback (preferred)

| Layer | Rollback method |
|-------|-----------------|
| Ubuntu packages | `sudo apt purge` specific stacks; keep distro |
| Python | Delete `~/ares-venv` and recreate |
| PX4 tree | `rm -rf ~/PX4-Autopilot` and re-clone pinned tag |
| ROS 2 | `sudo apt remove ros-humble-*` (last resort) |

### Hard rollback (WSL)

```powershell
wsl --shutdown
wsl --unregister Ubuntu-22.04
```

Then reinstall Ubuntu from Step 2. **Destroys the Linux filesystem.**

### Distro snapshot (recommended after Step 9 success)

```powershell
wsl --export Ubuntu-22.04 D:\backups\ares-ubuntu-22.04-phase0.tar
```

Restore later:

```powershell
wsl --import ARES-Ubuntu-22.04 D:\WSL\ARES D:\backups\ares-ubuntu-22.04-phase0.tar --version 2
```

### Windows restore point

Created in Step 0 (`Checkpoint-Computer`) if System Restore is enabled.

---

## 11. Disk Budget Estimate

| Component | Approx. size |
|-----------|--------------|
| Ubuntu 22.04 base | 2–3 GB |
| ROS 2 Humble desktop | 2–4 GB |
| Gazebo Harmonic | 1–2 GB |
| PX4 + toolchain + build | 8–15 GB |
| Logs / caches / venv | 2–5 GB |
| **Total comfortable free space** | **≥ 40 GB** |

Host has sufficient free space on C: and abundant space on D:/E:. Prefer keeping the WSL VHDX on a drive with ≥60 GB free long-term.

---

## 12. Phase 0 Exit Criteria

Phase 0 is **complete** when all are true:

- [ ] WSL2 + Ubuntu 22.04 running  
- [ ] ROS 2 Humble talker/listener works  
- [ ] Gazebo Harmonic launches  
- [ ] PX4 SITL `gz_x500` runs  
- [ ] MAVSDK Python arms, takes off, lands one simulated UAV  
- [ ] This document’s installed versions noted for the team  

**Out of scope for Phase 0:** autonomy algorithms, swarm, perception ML, LLM commander, ARES application modules.

---

## 13. Next Action (Human Gate)

**Awaiting confirmation before any installation.**

When approved, execute in order:

1. Steps 1–3 (Windows / WSL)  
2. Steps 4–9 (Ubuntu stack + verification)  
3. Export WSL snapshot (§10)  
4. Proceed to repository documentation package (`PROJECT_SPEC.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `DEVELOPMENT_RULES.md`) if not already created  

Reply with confirmation to begin installation (full Phase 0, or step-by-step with pauses).
