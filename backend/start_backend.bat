@echo off
REM Start Backend FastAPI server
cd /d %~dp0
echo Starting FastAPI backend...
uvicorn vin_dtc_viewer.main:app --reload --host 127.0.0.1 --port 8000
pause
