
@echo off
cd /d %~dp0
uvicorn vin_dtc_viewer.main:app --reload
pause
