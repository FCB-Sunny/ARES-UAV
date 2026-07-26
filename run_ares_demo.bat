@echo off
setlocal
cd /d "%~dp0"
title ARES-UAV Phase-2 Demo
echo.
echo === ARES-UAV: Gazebo + PX4 + planned waypoint flight ===
echo     (A* from missions\navigate_demo.json)
echo.
echo Prerequisites: VcXsrv installed; WSL Ubuntu user "sunny"; ~/ares-venv with MAVSDK.
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
