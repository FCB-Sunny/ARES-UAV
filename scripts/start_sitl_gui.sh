#!/bin/bash
# Start Gazebo (GUI via VcXsrv) + PX4 SITL x500.
# Intended to be launched from Windows: run_ares_demo.bat / run_ares_demo.py
set +u
cd /home/sunny/PX4-Autopilot
source /opt/ros/humble/setup.bash

WIN_HOST=$(awk '/nameserver/{print $2; exit}' /etc/resolv.conf)
export DISPLAY="${WIN_HOST}:0.0"
export LIBGL_ALWAYS_INDIRECT=0
export QT_X11_NO_MITSHM=1
mkdir -p /tmp/runtime-sunny
export XDG_RUNTIME_DIR=/tmp/runtime-sunny

PX4_ROOT=/home/sunny/PX4-Autopilot
export GZ_SIM_RESOURCE_PATH="$PX4_ROOT/Tools/simulation/gz/models:$PX4_ROOT/Tools/simulation/gz/worlds"
export HEADLESS=0

echo "DISPLAY=$DISPLAY"
killall -q px4 2>/dev/null || true
killall -q gz gz-sim gz-sim-server ruby 2>/dev/null || true
sleep 2

echo "Starting Gazebo WITH GUI (watch for a window on Windows)..."
gz sim -r "$PX4_ROOT/Tools/simulation/gz/worlds/default.sdf" > /tmp/gz_gui_flight.log 2>&1 &
echo "gz pid=$!"

ready=0
i=0
while [ $i -lt 90 ]; do
  i=$((i+1))
  if gz topic -l 2>/dev/null | grep -q .; then
    echo "Gazebo ready ($i)"
    ready=1
    break
  fi
  sleep 1
done
if [ "$ready" != "1" ]; then
  echo "Gazebo GUI failed:"; tail -40 /tmp/gz_gui_flight.log; exit 1
fi
sleep 5

echo "Starting PX4 (standalone)..."
export PX4_GZ_STANDALONE=1
export PX4_SYS_AUTOSTART=4001
export PX4_SIM_MODEL=gz_x500
export PX4_GZ_MODEL=x500
export PX4_GZ_MODEL_POSE="0,0,0.3"

cd "$PX4_ROOT/build/px4_sitl_default"
./bin/px4 -d .
