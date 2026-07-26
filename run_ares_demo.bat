@echo off
setlocal
cd /d "%~dp0"
title ARES-UAV SITL Demo
echo.
echo === ARES-UAV: Gazebo 3D + PX4 + MAVSDK takeoff/land ===
echo.
python "%~dp0run_ares_demo.py"
set ERR=%ERRORLEVEL%
echo.
if %ERR% neq 0 (
  echo Demo finished with error code %ERR%.
) else (
  echo Demo finished OK.
)
echo.
pause
exit /b %ERR%
